"""
Email notification system for scrape completion alerts

Supports:
- Multiple recipient emails
- SMTP configuration
- Connection testing
- HTML/Plain text emails
- Scrape completion notifications
"""

import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class EmailNotifier:
    """Email notification service for scrape events"""

    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize email notifier with SMTP configuration

        Args:
            config: Dict with keys:
                - smtp_host: SMTP server hostname (e.g., 'smtp.gmail.com')
                - smtp_port: SMTP port (465 for SSL, 587 for TLS, 25 for standard)
                - smtp_user: SMTP username/email
                - smtp_password: SMTP password or app password
                - smtp_use_tls: True/False (default: True for port 587)
                - smtp_use_ssl: True/False (default: True for port 465)
                - from_email: Sender email address
                - from_name: Sender name (optional)
        """
        self.config = config or {}
        self.enabled = bool(self.config.get('smtp_host'))

    def test_connection(self) -> Dict:
        """
        Test SMTP connection and authentication

        Returns:
            Dict with success status and message
        """
        if not self.enabled:
            return {
                'success': False,
                'message': 'SMTP not configured'
            }

        try:
            smtp_host = self.config.get('smtp_host')
            smtp_port = int(self.config.get('smtp_port', 587))
            smtp_user = self.config.get('smtp_user')
            smtp_password = self.config.get('smtp_password')
            use_tls = self.config.get('smtp_use_tls', smtp_port == 587)
            use_ssl = self.config.get('smtp_use_ssl', smtp_port == 465)

            if use_ssl:
                # Use SSL (port 465)
                server = smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=10)
            else:
                # Use standard connection, potentially upgrade to TLS
                server = smtplib.SMTP(smtp_host, smtp_port, timeout=10)
                if use_tls:
                    server.starttls()

            # Authenticate
            if smtp_user and smtp_password:
                server.login(smtp_user, smtp_password)

            server.quit()

            return {
                'success': True,
                'message': f'Successfully connected to {smtp_host}:{smtp_port}',
                'smtp_host': smtp_host,
                'smtp_port': smtp_port,
                'authenticated': bool(smtp_user)
            }

        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"SMTP authentication failed: {e}")
            return {
                'success': False,
                'message': 'Authentication failed. Check username/password',
                'error': str(e)
            }
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error: {e}")
            return {
                'success': False,
                'message': f'SMTP error: {str(e)}',
                'error': str(e)
            }
        except Exception as e:
            logger.error(f"Email connection test failed: {e}")
            return {
                'success': False,
                'message': f'Connection failed: {str(e)}',
                'error': str(e)
            }

    def send_scrape_completion(
        self,
        recipients: List[str],
        scrape_stats: Dict,
        workflow_url: Optional[str] = None
    ) -> Dict:
        """
        Send scrape completion notification email

        Args:
            recipients: List of email addresses
            scrape_stats: Dict with scrape statistics (site_count, properties_found, duration, etc.)
            workflow_url: Optional URL to GitHub Actions workflow run

        Returns:
            Dict with success status and details
        """
        if not self.enabled:
            return {
                'success': False,
                'message': 'Email notifications not configured'
            }

        if not recipients:
            return {
                'success': False,
                'message': 'No recipients specified'
            }

        try:
            # Create email
            subject = "✅ Real Estate Scrape Completed"
            html_body = self._generate_completion_email_html(scrape_stats, workflow_url)
            text_body = self._generate_completion_email_text(scrape_stats, workflow_url)

            # Send to all recipients
            results = []
            for recipient in recipients:
                result = self._send_email(
                    to_email=recipient,
                    subject=subject,
                    html_body=html_body,
                    text_body=text_body
                )
                results.append({'email': recipient, 'success': result['success']})

            successful = sum(1 for r in results if r['success'])

            return {
                'success': successful > 0,
                'message': f'Sent to {successful}/{len(recipients)} recipients',
                'results': results
            }

        except Exception as e:
            logger.error(f"Error sending scrape completion email: {e}")
            return {
                'success': False,
                'message': f'Error: {str(e)}',
                'error': str(e)
            }

    def _send_email(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        text_body: str
    ) -> Dict:
        """Send individual email"""
        try:
            smtp_host = self.config.get('smtp_host')
            smtp_port = int(self.config.get('smtp_port', 587))
            smtp_user = self.config.get('smtp_user')
            smtp_password = self.config.get('smtp_password')
            from_email = self.config.get('from_email', smtp_user)
            from_name = self.config.get('from_name', 'Realtors Practice Scraper')
            use_tls = self.config.get('smtp_use_tls', smtp_port == 587)
            use_ssl = self.config.get('smtp_use_ssl', smtp_port == 465)

            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f'"{from_name}" <{from_email}>'
            msg['To'] = to_email
            msg['Date'] = datetime.now().strftime('%a, %d %b %Y %H:%M:%S %z')

            # Attach both plain text and HTML versions
            msg.attach(MIMEText(text_body, 'plain'))
            msg.attach(MIMEText(html_body, 'html'))

            # Send via SMTP
            if use_ssl:
                server = smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=30)
            else:
                server = smtplib.SMTP(smtp_host, smtp_port, timeout=30)
                if use_tls:
                    server.starttls()

            if smtp_user and smtp_password:
                server.login(smtp_user, smtp_password)

            server.send_message(msg)
            server.quit()

            logger.info(f"Email sent successfully to {to_email}")
            return {'success': True, 'message': 'Email sent'}

        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return {'success': False, 'error': str(e)}

    def _generate_completion_email_html(self, stats: Dict, workflow_url: Optional[str]) -> str:
        """Generate HTML email body for scrape completion"""
        sites = stats.get('site_count', 0)
        properties = stats.get('properties_found', 0)
        duration = stats.get('duration', 'Unknown')
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        return f"""
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: #4CAF50; color: white; padding: 20px; text-align: center; border-radius: 5px 5px 0 0; }}
        .content {{ background: #f9f9f9; padding: 20px; border: 1px solid #ddd; }}
        .stats {{ background: white; padding: 15px; margin: 15px 0; border-radius: 5px; }}
        .stat-item {{ display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid #eee; }}
        .stat-label {{ font-weight: bold; }}
        .stat-value {{ color: #4CAF50; font-weight: bold; }}
        .button {{ display: inline-block; padding: 12px 24px; background: #4CAF50; color: white; text-decoration: none; border-radius: 5px; margin: 15px 0; }}
        .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>✅ Scrape Completed Successfully!</h1>
        </div>
        <div class="content">
            <p>Your real estate scraping session has finished. Here are the results:</p>

            <div class="stats">
                <div class="stat-item">
                    <span class="stat-label">Sites Scraped:</span>
                    <span class="stat-value">{sites}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Properties Found:</span>
                    <span class="stat-value">{properties:,}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Duration:</span>
                    <span class="stat-value">{duration}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Completed At:</span>
                    <span class="stat-value">{timestamp}</span>
                </div>
            </div>

            {"<p><a href='" + workflow_url + "' class='button'>View Workflow Details</a></p>" if workflow_url else ""}

            <p><strong>Next Steps:</strong></p>
            <ul>
                <li>Data has been uploaded to Firestore</li>
                <li>Cleaned exports available in GitHub Actions artifacts</li>
                <li>Query via: <code>POST /api/firestore/query</code></li>
            </ul>
        </div>
        <div class="footer">
            <p>Realtors Practice Scraper | Powered by GitHub Actions</p>
        </div>
    </div>
</body>
</html>
"""

    def _generate_completion_email_text(self, stats: Dict, workflow_url: Optional[str]) -> str:
        """Generate plain text email body for scrape completion"""
        sites = stats.get('site_count', 0)
        properties = stats.get('properties_found', 0)
        duration = stats.get('duration', 'Unknown')
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        text = f"""
SCRAPE COMPLETED SUCCESSFULLY!
================================

Your real estate scraping session has finished. Here are the results:

Sites Scraped: {sites}
Properties Found: {properties:,}
Duration: {duration}
Completed At: {timestamp}

"""
        if workflow_url:
            text += f"View Workflow Details: {workflow_url}\n\n"

        text += """
NEXT STEPS:
- Data has been uploaded to Firestore
- Cleaned exports available in GitHub Actions artifacts
- Query via: POST /api/firestore/query

---
Realtors Practice Scraper | Powered by GitHub Actions
"""
        return text
