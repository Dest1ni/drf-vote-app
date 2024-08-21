from .models import Survey,SurveyQuesiton,SurveyQuesitonOption,SurveyUser

def survey_exists(id:int) -> dict:
    try:
       survey = Survey.objects.get(pk = id)
       return {"exists": True,"survey":survey}
    except:
        return {"exists": False}
    
def question_exists(id:int) -> dict:
    try:
       question = SurveyQuesiton.objects.get(pk = id)
       return {"exists": True,"question":question}
    except:
        return {"exists": False}

def option_exists(id:int) -> dict:
    try:
       option = SurveyQuesitonOption.objects.get(pk = id)
       return {"exists": True,"option":option}
    except:
        return {"exists": False}

def survey_user_exists(id:int) -> dict:
    try:
       survey_user = SurveyUser.objects.get(pk = id)
       return {"exists": True,"survey_user":survey_user}
    except:
        return {"exists": False}    