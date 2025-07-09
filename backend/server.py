from fastapi import FastAPI, APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime
import base64
import io


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# Define Models for M&A Analysis
class StartupInput(BaseModel):
    startup_name: str
    description: str
    pitch_deck_images: Optional[List[str]] = []  # Base64 encoded images

class AcquirerInfo(BaseModel):
    name: str
    fit_percentage: int
    strategic_reasons: List[str]

class AnalysisResult(BaseModel):
    top_acquirers: List[AcquirerInfo]
    strategic_fit_summary: List[str]
    valuation_range: dict  # {"min": 10000000, "max": 50000000, "currency": "USD"}
    confidence_score: float
    analysis_timestamp: datetime = Field(default_factory=datetime.utcnow)

class StartupAnalysis(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    startup_name: str
    description: str
    pitch_deck_images: Optional[List[str]] = []
    analysis_result: Optional[AnalysisResult] = None
    status: str = "pending"  # pending, analyzing, completed, error
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# Existing models
class StatusCheck(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class StatusCheckCreate(BaseModel):
    client_name: str

# Placeholder function for LLM-powered M&A analysis
async def analyze_startup_with_llm(startup_name: str, description: str, images: List[str]) -> AnalysisResult:
    """
    Placeholder function for LLM-powered M&A analysis.
    In production, this would integrate with an LLM service to analyze the startup
    and provide acquisition recommendations.
    """
    # Mock analysis results for demonstration
    mock_acquirers = [
        AcquirerInfo(
            name="Microsoft",
            fit_percentage=85,
            strategic_reasons=[
                "Strong alignment with Azure cloud services",
                "Complementary technology stack",
                "Potential for enterprise customer cross-selling"
            ]
        ),
        AcquirerInfo(
            name="Google",
            fit_percentage=78,
            strategic_reasons=[
                "Enhanced AI/ML capabilities",
                "Strategic fit with Google Cloud platform",
                "Opportunity to strengthen developer tools"
            ]
        ),
        AcquirerInfo(
            name="Amazon",
            fit_percentage=72,
            strategic_reasons=[
                "AWS integration opportunities",
                "Expansion of service offerings",
                "Competitive advantage in cloud market"
            ]
        )
    ]
    
    mock_strategic_fit = [
        "Strong technical team with proven track record",
        "Scalable technology platform with growth potential",
        "Established customer base in target market",
        "Intellectual property portfolio with competitive advantages"
    ]
    
    # Simple valuation estimate (in practice, this would be much more sophisticated)
    base_valuation = len(description) * 100000  # Very basic mock calculation
    valuation_range = {
        "min": base_valuation,
        "max": base_valuation * 3,
        "currency": "USD"
    }
    
    return AnalysisResult(
        top_acquirers=mock_acquirers,
        strategic_fit_summary=mock_strategic_fit,
        valuation_range=valuation_range,
        confidence_score=0.73
    )

# M&A Analysis endpoints
@api_router.post("/analyze", response_model=StartupAnalysis)
async def analyze_startup(startup_input: StartupInput):
    """
    Analyze a startup for M&A opportunities.
    This endpoint processes the startup information and returns analysis results.
    """
    try:
        # Create analysis record
        analysis = StartupAnalysis(
            startup_name=startup_input.startup_name,
            description=startup_input.description,
            pitch_deck_images=startup_input.pitch_deck_images or [],
            status="analyzing"
        )
        
        # Store initial analysis record
        await db.startup_analyses.insert_one(analysis.dict())
        
        # Perform analysis (placeholder for LLM integration)
        analysis_result = await analyze_startup_with_llm(
            startup_input.startup_name,
            startup_input.description,
            startup_input.pitch_deck_images or []
        )
        
        # Update analysis with results
        analysis.analysis_result = analysis_result
        analysis.status = "completed"
        analysis.updated_at = datetime.utcnow()
        
        # Update in database
        await db.startup_analyses.update_one(
            {"id": analysis.id},
            {"$set": analysis.dict()}
        )
        
        return analysis
        
    except Exception as e:
        logger.error(f"Error analyzing startup: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@api_router.get("/analysis/{analysis_id}", response_model=StartupAnalysis)
async def get_analysis(analysis_id: str):
    """
    Retrieve analysis results by ID.
    """
    try:
        analysis = await db.startup_analyses.find_one({"id": analysis_id})
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        return StartupAnalysis(**analysis)
        
    except Exception as e:
        logger.error(f"Error retrieving analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve analysis: {str(e)}")

@api_router.get("/analyses", response_model=List[StartupAnalysis])
async def get_all_analyses():
    """
    Retrieve all startup analyses.
    """
    try:
        analyses = await db.startup_analyses.find().to_list(1000)
        return [StartupAnalysis(**analysis) for analysis in analyses]
        
    except Exception as e:
        logger.error(f"Error retrieving analyses: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve analyses: {str(e)}")

@api_router.post("/upload-image")
async def upload_pitch_deck_image(file: UploadFile = File(...)):
    """
    Upload a pitch deck image and return base64 encoded string.
    """
    try:
        # Validate file type
        if not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Read file content
        contents = await file.read()
        
        # Convert to base64
        base64_image = base64.b64encode(contents).decode('utf-8')
        
        return {
            "success": True,
            "image_data": f"data:{file.content_type};base64,{base64_image}",
            "filename": file.filename
        }
        
    except Exception as e:
        logger.error(f"Error uploading image: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Image upload failed: {str(e)}")

# Existing endpoints
@api_router.get("/")
async def root():
    return {"message": "Hello World"}

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.dict()
    status_obj = StatusCheck(**status_dict)
    _ = await db.status_checks.insert_one(status_obj.dict())
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db.status_checks.find().to_list(1000)
    return [StatusCheck(**status_check) for status_check in status_checks]

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
