from fastapi import APIRouter, Depends, HTTPException, status, Request
from app.models.user import User
from app.schemas.scenario import WhatIfRequest, ScenarioComparison
from app.services.scenario_service import ScenarioService
from app.api.dependencies import get_current_user

router = APIRouter(prefix="/scenarios", tags=["what-if-scenarios"])

@router.post("/what-if", response_model=ScenarioComparison)
async def run_what_if_analysis(
    request: Request,
    what_if_request: WhatIfRequest,
    current_user: User = Depends(get_current_user)
):
    """Run what-if scenario analysis comparing baseline to scenario"""
    try:
        if what_if_request.base_budget <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Base budget must be greater than 0"
            )
        
        comparison = await ScenarioService.run_what_if_analysis(
            current_user.clerk_user_id,
            what_if_request
        )
        return comparison
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        print(f"Error in what-if analysis: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to run what-if analysis: {str(e)}"
        )