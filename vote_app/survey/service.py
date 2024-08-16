from .models import Survey

def survey_exists(pk:int) -> dict:
    try:
       survey = Survey.objects.get(pk = pk)
       return {"exists": True,"survey":survey}
    except:
        return {"exists": False}