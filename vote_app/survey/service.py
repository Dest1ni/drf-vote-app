from .models import Survey

def survey_exists(id:int) -> dict:
    try:
       survey = Survey.objects.get(pk = id)
       return {"exists": True,"survey":survey}
    except:
        return {"exists": False}