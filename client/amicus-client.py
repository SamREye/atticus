from app import app, db
from app.models import User, Contract, Party, Template, ActivityLog, DealMessage

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Contract': Contract, "Party": Party, "Template": Template, "ActivityLog": ActivityLog, "DealMessage": DealMessage}
