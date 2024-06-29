from datetime import datetime

def get_current_shift():
    now = datetime.now()
    shift_end = now.replace(hour=15, minute=15, second=0, microsecond=0) # 3.15 pm
    return "shiftA" if now < shift_end else "shiftB"