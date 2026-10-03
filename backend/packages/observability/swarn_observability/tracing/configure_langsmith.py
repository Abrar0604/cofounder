import os

def configure_langsmith(settings) -> None:
    api_key = getattr(settings, 'langsmith_api_key', os.getenv("LANGSMITH_API_KEY"))
    tracing_enabled = getattr(settings, 'tracing_enabled', True)
    
    if api_key and tracing_enabled:
        os.environ["LANGSMITH_TRACING"] = "true"
        os.environ["LANGSMITH_API_KEY"] = api_key
        
        project = getattr(settings, 'langsmith_project', "swarn")
        os.environ["LANGSMITH_PROJECT"] = project
        
        env = getattr(settings, 'app_env', os.getenv("APP_ENV", "development"))
        if env.lower() == "production":
            os.environ["LANGSMITH_HIDE_INPUTS"] = "true"
            os.environ["LANGSMITH_HIDE_OUTPUTS"] = "true"
