from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import random
import time
from datetime import datetime
import asyncio

app = FastAPI(title="Cyberpunk FinOps Core API")

# Allow React app running on any port (e.g. 5173) to communicate with this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ClusterState:
    def __init__(self):
        self.status = "HEALTHY"
        self.offline_nodes = []
        self.active_anomaly_node = None
        self.savings = 14.40
        self.logs = [{
            "id": 1,
            "timestamp": datetime.now().strftime("%I:%M:%S %p"),
            "resourceId": "i-0abcd1234efgh5678",
            "reason": "Idle > 24h",
            "action": "Autonomously Stopped Instance"
        }]
        self.chart_data = []
        # Prime the initial chart historical data
        for i in range(15):
            self.chart_data.append({
                "time": f"T-{15-i}",
                "actualCost": random.uniform(10, 12),
                "projectedCost": random.uniform(10, 12),
            })
        self.is_simulating = False

state = ClusterState()

@app.on_event("startup")
async def startup_event():
    # Start the continuous chart ticker background task
    asyncio.create_task(background_chart_ticker())

async def background_chart_ticker():
    """Generates continuous 'healthy' fluctuation metrics for the graph every 2 seconds"""
    while True:
        await asyncio.sleep(2.0)
        if state.status == "HEALTHY" and not state.is_simulating:
            active_count = 8 - len(state.offline_nodes)
            base_cost = 0 if active_count == 0 else (active_count * 1.2) + random.uniform(0, 1)
            projected = 0 if active_count == 0 else base_cost + random.uniform(0, 0.5)
            
            state.chart_data.pop(0)
            state.chart_data.append({
                "time": datetime.now().strftime("%H:%M:%S"),
                "actualCost": round(base_cost, 2),
                "projectedCost": round(projected, 2)
            })

@app.get("/api/cluster")
async def get_cluster_state():
    """React UI polls this endpoint to get the entire global synchronized state"""
    return {
        "status": state.status,
        "offlineNodes": state.offline_nodes,
        "activeAnomalyNode": state.active_anomaly_node,
        "savings": state.savings,
        "logs": state.logs,
        "chartData": state.chart_data,
        "isSimulating": state.is_simulating
    }

@app.post("/api/chaos")
async def trigger_chaos():
    """Receives the attack command from React and initiates the background sequence"""
    if state.is_simulating:
        return {"msg": "Already simulating"}
    
    available = [n for n in range(8) if n not in state.offline_nodes]
    if not available:
        return {"msg": "All offline"}
    
    target_node = random.choice(available)
    state.active_anomaly_node = target_node
    state.is_simulating = True
    
    asyncio.create_task(chaos_sequence(target_node))
    return {"msg": "Chaos initiated"}

async def chaos_sequence(target_node: int):
    """The choreographed simulation, entirely migrated to the Python Server!"""
    # T=0s
    state.status = "ANOMALY"
    state.chart_data.pop(0)
    state.chart_data.append({"time": datetime.now().strftime("%H:%M:%S"), "actualCost": 85.0, "projectedCost": 85.0})
    
    # T=3s
    await asyncio.sleep(3.0)
    state.status = "REMEDIATING"
    state.chart_data.pop(0)
    state.chart_data.append({"time": datetime.now().strftime("%H:%M:%S"), "actualCost": 80.0, "projectedCost": 88.0})
    
    # T=5s
    await asyncio.sleep(2.0)
    state.status = "HEALTHY"
    
    new_active = 8 - len(state.offline_nodes) - 1
    drop_cost = 0 if new_active == 0 else (new_active * 1.2)
    
    state.chart_data.pop(0)
    state.chart_data.append({"time": datetime.now().strftime("%H:%M:%S"), "actualCost": round(drop_cost, 2), "projectedCost": 90.0})
    
    state.offline_nodes.append(target_node)
    act_log = {
        "id": int(time.time() * 1000),
        "timestamp": datetime.now().strftime("%I:%M:%S %p"),
        "resourceId": f"i-core-node-{target_node}",
        "reason": "CPU > 95% (Cost Spike)",
        "action": "Autonomously Stopped Instance"
    }
    state.logs.insert(0, act_log)
    state.savings += 75.50
    state.active_anomaly_node = None
    state.is_simulating = False

@app.post("/api/recover")
async def trigger_recovery():
    if state.is_simulating or len(state.offline_nodes) == 0:
        return {"msg": "invalid"}
        
    count = len(state.offline_nodes)
    state.offline_nodes = []
    
    act_log = {
        "id": int(time.time() * 1000),
        "timestamp": datetime.now().strftime("%I:%M:%S %p"),
        "resourceId": "auto-scaling-group",
        "reason": "Capacity Rebalanced",
        "action": f"Spun up {count} Replacement Node{'s' if count>1 else ''}"
    }
    state.logs.insert(0, act_log)
    return {"msg": "Recovered"}
