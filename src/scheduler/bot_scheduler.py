"""Bot scheduler for automated comment posting.

Manages scheduling and execution of comment tasks across all agents.
"""

import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger

from src.config import config
from src.database import db
from src.logger import log
from src.bot.tiktok_bot import TikTokBot
from src.ai.comment_generator import comment_generator


class BotScheduler:
    """Manages automated comment scheduling for all agents."""

    def __init__(self):
        """Initialize the scheduler."""
        self.scheduler = BackgroundScheduler()
        self.running_bots: Dict[int, TikTokBot] = {}
        self.is_running = False

    def start(self):
        """Start the scheduler and schedule tasks for all agents."""
        if self.is_running:
            log.warning("Scheduler is already running")
            return

        log.info("Starting bot scheduler...")
        self.scheduler.start()
        self.is_running = True

        # Schedule tasks for all active agents
        agents = db.get_all_agents()
        active_agents = [a for a in agents if a.status in ["idle", "active"]]

        if not active_agents:
            log.warning("No active agents found")
            return

        log.info(f"Scheduling tasks for {len(active_agents)} agent(s)")

        for agent in active_agents:
            self._schedule_agent_tasks(agent.id)

        log.success(f"Scheduler started with {len(active_agents)} agent(s)")

    def stop(self):
        """Stop the scheduler and cleanup."""
        if not self.is_running:
            log.warning("Scheduler is not running")
            return

        log.info("Stopping bot scheduler...")
        self.scheduler.shutdown(wait=False)
        self.is_running = False

        # Clean up any running bots
        for bot in self.running_bots.values():
            try:
                bot.cleanup()
            except Exception as e:
                log.error(f"Error cleaning up bot: {e}")

        self.running_bots.clear()
        log.success("Scheduler stopped")

    def _schedule_agent_tasks(self, agent_id: int):
        """Schedule comment tasks for a specific agent.

        Args:
            agent_id: ID of the agent to schedule tasks for
        """
        agent = db.get_agent(agent_id)
        if not agent:
            log.error(f"Agent {agent_id} not found")
            return

        # Get number of comments to post today
        comments_target = config.COMMENTS_PER_DAY
        comments_posted = agent.comments_today

        if comments_posted >= comments_target:
            log.info(f"[Agent {agent_id}] Already reached daily limit ({comments_posted}/{comments_target})")
            # Schedule first comment for tomorrow
            tomorrow = datetime.now() + timedelta(days=1)
            next_run = tomorrow.replace(hour=random.randint(8, 23), minute=random.randint(0, 59), second=0)
            db.update_agent_next_run(agent_id, next_run)
            self._schedule_single_comment(agent_id, next_run)
            return

        # Calculate remaining comments for today
        remaining = comments_target - comments_posted
        log.info(f"[Agent {agent_id}] Scheduling {remaining} comment(s) for today")

        # Distribute comments throughout the day
        schedule_times = self._generate_schedule_times(remaining)

        for run_time in schedule_times:
            self._schedule_single_comment(agent_id, run_time)

        # Update agent's next run time
        if schedule_times:
            db.update_agent_next_run(agent_id, schedule_times[0])

    def _generate_schedule_times(self, num_comments: int) -> List[datetime]:
        """Generate random schedule times for comments.

        Args:
            num_comments: Number of comments to schedule

        Returns:
            List of datetime objects representing when to post comments
        """
        now = datetime.now()
        end_of_day = now.replace(hour=23, minute=59, second=59)

        # Calculate time window
        remaining_minutes = (end_of_day - now).total_seconds() / 60

        if remaining_minutes < config.MIN_DELAY_MINUTES * num_comments:
            # Not enough time today, schedule fewer comments
            num_comments = max(1, int(remaining_minutes / config.MIN_DELAY_MINUTES))
            log.warning(f"Reduced comments to {num_comments} due to time constraints")

        schedule_times = []
        current_time = now + timedelta(minutes=random.randint(1, 5))  # Start soon

        for i in range(num_comments):
            # Random delay between MIN and MAX
            delay_minutes = random.randint(
                config.MIN_DELAY_MINUTES,
                config.MAX_DELAY_MINUTES
            )

            current_time = current_time + timedelta(minutes=delay_minutes)

            # Don't schedule past end of day
            if current_time > end_of_day:
                break

            schedule_times.append(current_time)

        return schedule_times

    def _schedule_single_comment(self, agent_id: int, run_time: datetime):
        """Schedule a single comment task.

        Args:
            agent_id: ID of the agent
            run_time: When to run the task
        """
        job_id = f"agent_{agent_id}_{run_time.timestamp()}"

        self.scheduler.add_job(
            func=self._execute_comment_task,
            trigger=DateTrigger(run_date=run_time),
            args=[agent_id],
            id=job_id,
            replace_existing=True
        )

        log.info(f"[Agent {agent_id}] Scheduled comment for {run_time.strftime('%H:%M:%S')}")

    def _execute_comment_task(self, agent_id: int):
        """Execute a comment task for an agent.

        Args:
            agent_id: ID of the agent to run
        """
        log.info(f"[Agent {agent_id}] Starting comment task...")

        try:
            # Get agent details
            agent = db.get_agent(agent_id)
            if not agent:
                log.error(f"[Agent {agent_id}] Agent not found")
                return

            if agent.status == "banned":
                log.warning(f"[Agent {agent_id}] Agent is banned, skipping")
                return

            # Update status
            db.update_agent_status(agent_id, "active")

            # Get credentials
            password = db.get_agent_password(agent_id)

            # Create bot instance
            bot = TikTokBot(
                agent_id=agent_id,
                username=agent.username,
                password=password
            )

            # Run comment cycle with AI generation
            result = self._run_comment_with_ai(bot)

            # Handle result
            if result["status"] == "success":
                log.success(f"[Agent {agent_id}] Comment posted successfully!")

                # Update database
                db.increment_agent_comments(agent_id)
                db.log_comment(
                    agent_id=agent_id,
                    video_url=result["video_info"].get("url", ""),
                    comment_text=result["comment"],
                    status="success"
                )

                # Schedule next comment if under daily limit
                agent = db.get_agent(agent_id)  # Refresh data
                if agent.comments_today < config.COMMENTS_PER_DAY:
                    delay_minutes = random.randint(
                        config.MIN_DELAY_MINUTES,
                        config.MAX_DELAY_MINUTES
                    )
                    next_run = datetime.now() + timedelta(minutes=delay_minutes)
                    self._schedule_single_comment(agent_id, next_run)
                    db.update_agent_next_run(agent_id, next_run)
                else:
                    log.info(f"[Agent {agent_id}] Daily limit reached")
                    db.update_agent_status(agent_id, "idle")

            else:
                log.error(f"[Agent {agent_id}] Comment failed: {result['error']}")
                db.log_comment(
                    agent_id=agent_id,
                    video_url=result["video_info"].get("url", "") if result["video_info"] else "",
                    comment_text="",
                    status="failed",
                    error_message=result["error"]
                )

                # Set agent to error status
                db.update_agent_status(agent_id, "error")

        except Exception as e:
            log.error(f"[Agent {agent_id}] Error executing comment task: {e}")
            db.update_agent_status(agent_id, "error")
            db.log_comment(
                agent_id=agent_id,
                video_url="",
                comment_text="",
                status="failed",
                error_message=str(e)
            )

    def _run_comment_with_ai(self, bot: TikTokBot) -> Dict:
        """Run a complete comment cycle with AI-generated content.

        Args:
            bot: TikTokBot instance

        Returns:
            Result dictionary with status, video_info, comment, error
        """
        try:
            # Login if needed
            if not bot.login():
                return {
                    "status": "failed",
                    "video_info": None,
                    "comment": "",
                    "error": "Login failed"
                }

            # Navigate to Explore page for variety
            if not bot.navigate_to_explore():
                return {
                    "status": "failed",
                    "video_info": None,
                    "comment": "",
                    "error": "Navigation failed"
                }

            # Click into a video to open full view
            if not bot.click_into_video():
                bot._save_session()
                bot._close_browser()
                return {
                    "status": "failed",
                    "video_info": None,
                    "comment": "",
                    "error": "Could not click into video"
                }

            # Extract video info
            video_info = bot.get_video_info()
            if not video_info:
                bot._save_session()
                bot._close_browser()
                return {
                    "status": "failed",
                    "video_info": None,
                    "comment": "",
                    "error": "Could not extract video info"
                }

            log.info(f"[Agent {bot.agent_id}] Video: {video_info.get('url', 'Unknown')}")

            # Generate AI comment
            comment = comment_generator.generate_comment(
                video_description=video_info.get("description", ""),
                creator_name=video_info.get("creator", ""),
                video_context=f"TikTok video"
            )

            log.info(f"[Agent {bot.agent_id}] Generated comment: {comment}")

            # Post comment
            if bot.post_comment(comment):
                bot._save_session()
                bot._close_browser()
                return {
                    "status": "success",
                    "video_info": video_info,
                    "comment": comment,
                    "error": None
                }
            else:
                bot._save_session()
                bot._close_browser()
                return {
                    "status": "failed",
                    "video_info": video_info,
                    "comment": comment,
                    "error": "Failed to post comment"
                }

        except Exception as e:
            log.error(f"[Agent {bot.agent_id}] Error in comment cycle: {e}")
            bot._save_session()
            bot._close_browser()
            return {
                "status": "failed",
                "video_info": None,
                "comment": "",
                "error": str(e)
            }

    def get_status(self) -> Dict:
        """Get current scheduler status.

        Returns:
            Dictionary with scheduler information
        """
        agents = db.get_all_agents()
        active_agents = [a for a in agents if a.status in ["idle", "active"]]

        jobs = self.scheduler.get_jobs() if self.is_running else []

        return {
            "running": self.is_running,
            "total_agents": len(agents),
            "active_agents": len(active_agents),
            "scheduled_jobs": len(jobs),
            "agents": [
                {
                    "id": a.id,
                    "username": a.username,
                    "status": a.status,
                    "comments_today": a.comments_today,
                    "next_run": a.next_run.strftime("%H:%M:%S") if a.next_run else "Not scheduled"
                }
                for a in active_agents
            ]
        }


# Singleton instance
bot_scheduler = BotScheduler()
