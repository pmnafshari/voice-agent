_pending_command = None
_last_action = None

def set_pending_command(command: dict):
    global _pending_command
    _pending_command = command

def get_pending_command():
    return _pending_command

def clear_pending_command():
    global _pending_command
    _pending_command = None

def set_last_action(action: dict):
    global _last_action
    _last_action = action

def get_last_action():
    return _last_action

def clear_last_action():
    global _last_action
    _last_action = None