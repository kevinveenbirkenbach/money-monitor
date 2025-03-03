
from datetime import datetime,date

def createComparatableTime(date_and_or_time)->datetime:
    # If it's a date (but not datetime), convert it to datetime
    
    if isinstance(date_and_or_time, date) and not isinstance(date_and_or_time, datetime):
        return datetime.combine(date_and_or_time, datetime.min.time())

    # If it's already a datetime, ensure it's naive (remove timezone info if it's aware)
    if isinstance(date_and_or_time, datetime):
        if date_and_or_time.tzinfo is not None:
            return date_and_or_time.replace(tzinfo=None)  # Convert aware datetime to naive datetime
        return date_and_or_time  # It's already naive, so return as is
    
    raise ValueError(f"Unexpected type: {type(date_and_or_time)}, value: {date_and_or_time}")  # Handle unexpected types    
