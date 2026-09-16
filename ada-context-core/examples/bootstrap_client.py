import os, requests
base=os.getenv('ADA_CORE_URL','http://127.0.0.1:8791')
h={'X-Ada-Internal-Key':os.environ['ADA_INTERNAL_API_KEY']}
r=requests.post(base+'/v1/bootstrap',headers=h,json={'agent_id':'mistral-shadow','task_type':'academic_content','project_id':'teznevise','site_id':'teznevise.ir'})
r.raise_for_status(); print(r.json())
