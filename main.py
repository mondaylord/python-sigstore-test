import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dstack_sdk import DstackClient

# The response structure for the /quote endpoint.
class QuoteResponse(BaseModel):
    quote: str
    event_log: str

# Initialize the FastAPI app.
app = FastAPI()

# Initialize the D-Stack client. It will use the default socket path
# or the DSTACK_SIMULATOR_ENDPOINT environment variable if set.
client = DstackClient()

@app.get("/quote", response_model=QuoteResponse)
async def get_quote():
    """Handler for the `/quote` endpoint.
    Returns a TEE quote and the corresponding event log.
    """
    try:
        quote_data = await client.get_quote()
        return QuoteResponse(quote=quote_data.quote, event_log=quote_data.event_log)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/info")
async def get_info():
    """Handler for the `/info` endpoint.
    Returns the `app_compose` information from the TCB info.
    """
    try:
        info = await client.info()
        # The Python SDK returns a Pydantic model which can be converted to a dict.
        info_dict = info.dict()
        tcb_info = info_dict.get("tcb_info", {})
        app_compose = tcb_info.get("app_compose")

        if app_compose is not None:
            return app_compose
        else:
            raise HTTPException(
                status_code=404, detail="app_compose not found in tcb_info"
            )
    except Exception as e:
        # If it's an HTTPException we raised, re-raise it.
        if isinstance(e, HTTPException):
            raise e
        # Otherwise, wrap it in a 500 error.
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
