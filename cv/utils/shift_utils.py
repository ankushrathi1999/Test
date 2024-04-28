from datetime import datetime

def get_current_shift():
    now = datetime.now()
    shift_end = now.replace(hour=15, minute=30, second=0, microsecond=0) # 3.30 pm
    return "shiftA" if now < shift_end else "shiftB"