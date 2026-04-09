import logging
from fastapi import APIRouter, HTTPException, status
from .schemas import ContactRequest, ContactResponse
from .email_utils import send_helpdesk_email

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/helpdesk", tags=["helpdesk"])


@router.post("/contact", response_model=ContactResponse)
async def contact_helpdesk(data: ContactRequest):
    """
    Accepts a contact form submission and emails it to the organization helpdesk.
    """
    try:
        await send_helpdesk_email(
            name=data.name,
            sender_email=data.email,
            message=data.message,
        )
        return ContactResponse(
            success=True,
            message="Your message has been sent to our helpdesk. We will contact you soon."
        )
    except Exception as e:
        logger.error(f"Helpdesk contact endpoint error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send your message. Please try again later."
        )
