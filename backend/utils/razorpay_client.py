import os
import razorpay

_razorpay_client: razorpay.Client | None = None

def get_razorpay_client() -> razorpay.Client:
    """Create or return a cached Razorpay client."""
    global _razorpay_client
    if _razorpay_client is None:
        key_id = os.getenv("RAZORPAY_KEY_ID")
        key_secret = os.getenv("RAZORPAY_KEY_SECRET")
        if not key_id or not key_secret:
            raise RuntimeError("Razorpay credentials are not configured")
        _razorpay_client = razorpay.Client(auth=(key_id, key_secret))
    return _razorpay_client
