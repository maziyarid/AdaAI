from __future__ import annotations
import os
import httpx
from fastmcp import FastMCP

CORE=os.environ.get('ADA_CORE_URL','http://127.0.0.1:8791')
KEY=os.environ.get('ADA_INTERNAL_API_KEY','')
if len(KEY)<32: raise RuntimeError('ADA_INTERNAL_API_KEY required')
H={'X-Ada-Internal-Key':KEY}
mcp=FastMCP('Ada Context MCP')

async def post(path,payload):
    async with httpx.AsyncClient(timeout=30) as c:
        r=await c.post(CORE+path,json=payload,headers=H); r.raise_for_status(); return r.json()
async def get(path):
    async with httpx.AsyncClient(timeout=30) as c:
        r=await c.get(CORE+path,headers=H); r.raise_for_status(); return r.json()

@mcp.tool
def context_status() -> dict:
    """Check authoritative Context Core health/version."""
    with httpx.Client(timeout=10) as c:
        r=c.get(CORE+'/healthz'); r.raise_for_status(); return r.json()

@mcp.tool
async def context_bootstrap(agent_id:str,task_type:str,project_id:str|None=None,site_id:str|None=None,project_lane:str='main',task_run_id:str|None=None)->dict:
    """Mandatory bootstrap for a task. Returns exact P0/P1 context and a scoped freshness receipt."""
    return await post('/v1/bootstrap',{'agent_id':agent_id,'task_type':task_type,'project_id':project_id,'site_id':site_id,
                                       'project_lane':project_lane,'task_run_id':task_run_id})

@mcp.tool
async def context_validate_receipt(receipt_id:str)->dict:
    """Validate a Context Core receipt before a consequential action."""
    return await get(f'/v1/receipts/{receipt_id}/validate')

@mcp.tool
async def context_propose_memory(canonical_key:str,record_type:str,scope_type:str,scope_id:str,title:str,content:str,created_by:str,
                                 priority:int=4,privacy_class:str='LOCAL_ONLY',source_reference:str|None=None)->dict:
    """Store an agent-proposed memory as CANDIDATE only. This never creates P0/P1 canonical policy."""
    priority=max(2,min(5,priority))
    return await post('/v1/memory/upsert',{'canonical_key':canonical_key,'record_type':record_type,'scope_type':scope_type,'scope_id':scope_id,
      'priority':priority,'authority':'agent_inference','provenance':'PROPOSED','privacy_class':privacy_class,'title':title,'content':content,
      'source_reference':source_reference,'created_by':created_by,'reason':'agent proposal','status':'CANDIDATE'})

@mcp.tool
async def context_checkpoint(project_id:str,lane:str,updated_by:str,objective:str|None=None,verified_status:str|None=None,
                             next_action:str|None=None,completed_work:list|None=None,blockers:list|None=None,pending_qa:list|None=None)->dict:
    """Update resumable project state. This is working state, not durable canonical policy."""
    return await post('/v1/state/update',{'project_id':project_id,'lane':lane,'updated_by':updated_by,'objective':objective,
      'verified_status':verified_status,'next_action':next_action,'completed_work':completed_work or [],'active_decisions':[],
      'blockers':blockers or [],'active_artifacts':[],'pending_qa':pending_qa or []})

if __name__=='__main__':
    mcp.run(transport='http',host='127.0.0.1',port=8792)
