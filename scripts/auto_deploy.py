#!/usr/bin/env python3
"""
Automated Deployment Agent Skill
================================
A reusable intelligence script that validates builds and auto-deploys on success.

This script acts as an autonomous deployment agent that:
1. Runs the build process to catch broken links and errors
2. On success: automatically stages, commits, and pushes changes
3. On failure: reports detailed error information for debugging

Usage:
    python scripts/auto_deploy.py
    python scripts/auto_deploy.py --message "Custom commit message"
"""

import subprocess
import sys
import argparse
from datetime import datetime
from typing import Tuple, Optional


class DeploymentAgent:
    """Autonomous agent for validating and deploying documentation builds."""

    def __init__(self, commit_message: Optional[str] = None):
        self.commit_message = commit_message or f"Auto-deploy via Agent Skill - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        self.build_output = ""
        self.error_output = ""

    def log(self, message: str, level: str = "INFO") -> None:
        """Print formatted log messages."""
        icons = {
            "INFO": "[i]",
            "SUCCESS": "[+]",
            "ERROR": "[!]",
            "WORKING": "[*]"
        }
        icon = icons.get(level, "")
        print(f"{icon} [{level}] {message}")

    def run_command(self, command: list, description: str) -> Tuple[bool, str, str]:
        """Execute a shell command and return success status with output."""
        self.log(f"{description}...", "WORKING")

        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                shell=True if sys.platform == "win32" else False
            )

            stdout = result.stdout.strip()
            stderr = result.stderr.strip()
            success = result.returncode == 0

            return success, stdout, stderr

        except Exception as e:
            return False, "", str(e)

    def check_for_changes(self) -> bool:
        """Check if there are any changes to commit."""
        success, stdout, _ = self.run_command(
            ["git", "status", "--porcelain"],
            "Checking for changes"
        )
        return bool(stdout.strip())

    def run_build(self) -> bool:
        """Execute npm build and validate for errors."""
        self.log("Starting build validation...", "INFO")

        # Run npm build
        command = "npm run build" if sys.platform == "win32" else ["npm", "run", "build"]
        success, stdout, stderr = self.run_command(
            command if isinstance(command, list) else command.split(),
            "Running npm build"
        )

        self.build_output = stdout
        self.error_output = stderr

        if success:
            self.log("Build completed successfully!", "SUCCESS")
            return True
        else:
            self.log("Build failed!", "ERROR")
            return False

    def stage_changes(self) -> bool:
        """Stage all changes for commit."""
        success, _, stderr = self.run_command(
            ["git", "add", "."],
            "Staging changes"
        )

        if success:
            self.log("Changes staged successfully", "SUCCESS")
        else:
            self.log(f"Failed to stage changes: {stderr}", "ERROR")

        return success

    def commit_changes(self) -> bool:
        """Create a commit with the deployment message."""
        success, _, stderr = self.run_command(
            ["git", "commit", "-m", self.commit_message],
            "Creating commit"
        )

        if success:
            self.log(f"Committed: {self.commit_message}", "SUCCESS")
        else:
            if "nothing to commit" in stderr.lower():
                self.log("No changes to commit", "INFO")
                return True
            self.log(f"Failed to commit: {stderr}", "ERROR")

        return success

    def push_changes(self) -> bool:
        """Push committed changes to remote."""
        success, stdout, stderr = self.run_command(
            ["git", "push"],
            "Pushing to remote"
        )

        if success:
            self.log("Successfully pushed to remote!", "SUCCESS")
        else:
            self.log(f"Failed to push: {stderr}", "ERROR")

        return success

    def report_build_errors(self) -> None:
        """Display detailed build error information."""
        print("\n" + "=" * 60)
        print("BUILD ERROR REPORT")
        print("=" * 60)

        if self.error_output:
            print("\n[STDERR Output]")
            print("-" * 40)
            print(self.error_output)

        if self.build_output:
            print("\n[STDOUT Output]")
            print("-" * 40)
            # Show last 50 lines of build output for context
            lines = self.build_output.split('\n')
            if len(lines) > 50:
                print(f"... (showing last 50 of {len(lines)} lines)")
                lines = lines[-50:]
            print('\n'.join(lines))

        print("\n" + "=" * 60)
        print("COMMON ISSUES TO CHECK:")
        print("=" * 60)
        print("1. Broken internal links (check file paths)")
        print("2. Missing images or assets")
        print("3. Invalid markdown syntax")
        print("4. Missing frontmatter in docs")
        print("5. JavaScript/TypeScript errors in components")
        print("=" * 60 + "\n")

    def deploy(self) -> bool:
        """Execute the full deployment pipeline."""
        print("\n" + "=" * 60)
        print("AUTOMATED DEPLOYMENT AGENT")
        print("=" * 60 + "\n")

        # Step 1: Run build validation
        if not self.run_build():
            self.report_build_errors()
            self.log("Deployment aborted due to build failure", "ERROR")
            return False

        # Step 2: Check for changes
        if not self.check_for_changes():
            self.log("No changes detected. Nothing to deploy.", "INFO")
            return True

        # Step 3: Stage changes
        if not self.stage_changes():
            self.log("Deployment aborted: failed to stage changes", "ERROR")
            return False

        # Step 4: Commit changes
        if not self.commit_changes():
            self.log("Deployment aborted: failed to commit", "ERROR")
            return False

        # Step 5: Push to remote
        if not self.push_changes():
            self.log("Deployment aborted: failed to push", "ERROR")
            return False

        print("\n" + "=" * 60)
        self.log("DEPLOYMENT COMPLETE!", "SUCCESS")
        print("=" * 60 + "\n")

        return True


def main():
    """Main entry point for the deployment agent."""
    parser = argparse.ArgumentParser(
        description="Automated Deployment Agent - Validates build and auto-deploys on success"
    )
    parser.add_argument(
        "-m", "--message",
        type=str,
        help="Custom commit message (default: auto-generated with timestamp)"
    )

    args = parser.parse_args()

    agent = DeploymentAgent(commit_message=args.message)
    success = agent.deploy()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
