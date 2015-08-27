__author__ = 'sisobus'

ALLOWED_EXTENSIONS = set(['txt','pdf','png','jpg','jpeg','gif'])

def allowedFile(filename):
    return '.' in filename and filename.rsplit('.',1)[1] in ALLOWED_EXTENSIONS