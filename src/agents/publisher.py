"""
Node E: The Publisher
Formats and delivers research insights via email.
"""
import logging
import os
import smtplib
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List

from src.core.models import AnalyzedPaper, EmailReport
from src.core.prompts import EMAIL_TEMPLATE_HTML, PAPER_CARD_HTML
from src.core.state import ResearchState
from src.tools.paper_tracker import PaperTracker

logger = logging.getLogger(__name__)


class PublisherAgent:
    """Agent that formats and delivers email reports."""
    
    def __init__(self):
        self.smtp_host = os.getenv('SMTP_HOST', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', 587))
        self.smtp_user = os.getenv('SMTP_USER')
        self.smtp_pass = os.getenv('SMTP_PASS')
        self.recipient = os.getenv('RECIPIENT_EMAIL')
        self.tracker = PaperTracker()
        
        # Cleanup old entries periodically
        history_days = int(os.getenv('PAPER_HISTORY_DAYS', 365))
        self.tracker.cleanup_old_entries(days_to_keep=history_days)
        
        if not all([self.smtp_user, self.smtp_pass, self.recipient]):
            logger.warning("SMTP credentials not fully configured")
    
    def run(self, state: ResearchState) -> ResearchState:
        """
        Execute the publisher node.
        
        Args:
            state: Current graph state
            
        Returns:
            Updated state with email delivery status
        """
        logger.info("📧 Running Publisher Agent...")
        
        if not state.get('analyzed_papers'):
            logger.warning("No analyzed papers to publish")
            return state
        
        try:
            papers_to_send = state['analyzed_papers']
            
            # Safety net: deduplicate by title in this batch (rare edge case)
            # Note: Duplicates should already be removed in Analyst agent
            seen_titles = set()
            unique_papers = []
            duplicates_in_batch = 0
            
            for paper in papers_to_send:
                # Normalize title for comparison
                normalized_title = self.tracker.normalize_title(paper.metadata.title)
                
                if normalized_title in seen_titles:
                    duplicates_in_batch += 1
                    logger.warning(f"🚫 Late-stage duplicate detected: '{paper.metadata.title[:60]}...'")
                    logger.warning(f"   (This should have been caught in Analyst - potential bug!)")
                else:
                    seen_titles.add(normalized_title)
                    unique_papers.append(paper)
            
            if duplicates_in_batch > 0:
                logger.warning(f"⚠️  Removed {duplicates_in_batch} duplicates at Publisher stage (should be caught earlier)")
            
            papers_to_send = unique_papers
            
            if not papers_to_send:
                logger.info("📭 No papers to send")
                state['email_content'] = None
                return state
            
            logger.info(f"📨 Preparing to send {len(papers_to_send)} papers")
            
            # Generate email content
            email_report = self._generate_email(papers_to_send)
            state['email_content'] = email_report
            
            # Send email (unless skipped)
            if not state.get('skip_email', False):
                self._send_email(email_report)
                
                # Mark papers as sent AFTER successful delivery
                paper_ids = [p.metadata.openalex_id for p in papers_to_send]
                paper_titles = [p.metadata.title for p in papers_to_send]
                self.tracker.mark_multiple_as_sent(paper_ids, paper_titles)
                
                # Show tracking stats
                stats = self.tracker.get_stats()
                logger.info(f"✅ Email delivered to {self.recipient}")
                logger.info(f"📊 Total papers sent historically: {stats['total_sent']}")
            else:
                logger.info("📝 Email generated but not sent (skip_email=True)")
            
        except Exception as e:
            error_msg = f"Publisher failed: {e}"
            logger.error(error_msg)
            state['errors'].append(error_msg)
        
        return state
    
    def _generate_email(self, papers: List[AnalyzedPaper]) -> EmailReport:
        """
        Generate HTML and plain text email content.
        
        Args:
            papers: Analyzed papers to include
            
        Returns:
            EmailReport object
        """
        # Generate paper cards
        papers_html = []
        
        for paper in papers:
            score_class = 'high' if paper.borrowability_score >= 0.8 else 'medium'
            
            authors_str = ', '.join(paper.metadata.authors[:3])
            if len(paper.metadata.authors) > 3:
                authors_str += ' et al.'
            
            # Truncate abstract if too long (keep first 500 chars)
            abstract = paper.metadata.abstract or 'No abstract available.'
            # if len(abstract) > 500:
            #     abstract = abstract[:497] + '...'
            
            card_html = PAPER_CARD_HTML.format(
                title=paper.metadata.title,
                field=paper.metadata.primary_field or 'Unknown',
                authors=authors_str,
                date=paper.metadata.publication_date.strftime('%Y-%m-%d'),
                score=f"{paper.borrowability_score:.2f}",
                score_class=score_class,
                abstract=abstract,
                isomorphic_connection=paper.isomorphic_connection,
                methodology=paper.methodology_summary,
                practical_application=paper.practical_application,
                paper_url=paper.metadata.url or '#'
            )
            papers_html.append(card_html)
        
        # Combine into full email
        now = datetime.utcnow()
        next_scan = now + timedelta(days=7)
        
        html_body = EMAIL_TEMPLATE_HTML.format(
            report_date=now.strftime('%B %d, %Y'),
            papers_count=len(papers),
            papers_html='\n'.join(papers_html),
            next_scan_date=next_scan.strftime('%B %d, %Y')
        )
        
        # Generate plain text version
        plain_text_parts = [
            f"Academic Radar Report - {now.strftime('%B %d, %Y')}",
            f"Found {len(papers)} isomorphic discoveries\n",
            "=" * 60
        ]
        
        for i, paper in enumerate(papers, 1):
            # Truncate abstract for plain text
            abstract = paper.metadata.abstract or 'No abstract available.'
            if len(abstract) > 300:
                abstract = abstract[:297] + '...'
            
            plain_text_parts.extend([
                f"\n{i}. {paper.metadata.title}",
                f"   Field: {paper.metadata.primary_field} | Score: {paper.borrowability_score:.2f}",
                f"\n   Abstract: {abstract}",
                f"\n   {paper.isomorphic_connection}",
                f"\n   How to apply: {paper.practical_application}",
                f"   Read: {paper.metadata.url}\n"
            ])
        
        plain_text_body = '\n'.join(plain_text_parts)
        
        # Create subject line
        subject = f"🎯 Academic Radar: {len(papers)} Isomorphic Discoveries This Week"
        
        return EmailReport(
            subject=subject,
            html_body=html_body,
            plain_text_body=plain_text_body,
            papers_count=len(papers)
        )
    
    def _send_email(self, email_report: EmailReport):
        """
        Send email via SMTP.
        
        Args:
            email_report: Email content to send
        """
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = email_report.subject
        msg['From'] = self.smtp_user
        msg['To'] = self.recipient
        
        # Attach both plain text and HTML versions
        part1 = MIMEText(email_report.plain_text_body, 'plain')
        part2 = MIMEText(email_report.html_body, 'html')
        
        msg.attach(part1)
        msg.attach(part2)
        
        # Send via SMTP
        try:
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_pass)
                server.send_message(msg)
                
        except Exception as e:
            logger.error(f"SMTP error: {e}")
            raise


# Node function for LangGraph
def publisher_node(state: ResearchState) -> ResearchState:
    """LangGraph node wrapper for PublisherAgent."""
    agent = PublisherAgent()
    return agent.run(state)
