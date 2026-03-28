from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import random
import time
from datetime import datetime
import asyncio
import pandas as pd
from anomaly_detection.model import AnomalyDetector

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
    """The choreographed simulation, dynamically routed through the new Machine Learning Model!"""
    state.status = "ANOMALY"
    state.chart_data.pop(0)
    state.chart_data.append({"time": datetime.now().strftime("%H:%M:%S"), "actualCost": 85.0, "projectedCost": 85.0})
    await asyncio.sleep(2.0)
    
    # 1. Randomly pick a chaos attack vector
    attack_type = random.choice(["CPU_SPIKE", "ZOMBIE_MEMORY_LEAK", "DATA_EXFILTRATION_SPIKE"])
    
    # 2. Build healthy baseline history for the ML Model (14 hours)
    history = []
    for h in range(1, 15):
        history.append({
            "resource_id": f"node-{target_node}",
            "hour": str(h),
            "cpuutilization": random.uniform(10.0, 20.0),
            "memoryutilization": random.uniform(30.0, 45.0),
            "network_out_bytes": random.uniform(1000, 5000)
        })
        
    # 3. Inject the anomalous telemetry vector
    anomaly_point = {
        "resource_id": f"node-{target_node}",
        "hour": "15",
        "cpuutilization": 15.0,
        "memoryutilization": 40.0,
        "network_out_bytes": 2500
    }
    
    if attack_type == "CPU_SPIKE":
        anomaly_point["cpuutilization"] = 99.8
        action = "Autonomously Stopped Instance (Overload)"
    elif attack_type == "ZOMBIE_MEMORY_LEAK":
        anomaly_point["memoryutilization"] = 98.7
        anomaly_point["cpuutilization"] = 0.5  # Critical indicator of an idle zombie node leaking ram
        action = "Terminated Idle/Leaking Zombie Resource"
    else:
        anomaly_point["network_out_bytes"] = 85000000.0  # Massive network spike
        action = "Isolated Network Interface Constraint"
        
    history.append(anomaly_point)
    df = pd.DataFrame(history)
    
    # 4. SEND THROUGH THE AI: Core Isolation Forest Z-Score Evaluation
    detector = AnomalyDetector()
    results = detector.detect_from_dataframe(df, threshold=3.0)
    
    ml_reason = "Unidentified Anomaly Detected by Security"
    for r in results:
        if r["hour"] == "15" and r["anomaly"]:
            ml_reason = r["reason"] # Example AI generation: "memoryutilization deviated from normal baseline (score=5.41)"
            break
            
    # 5. UI Recovery Sequence Animation
    state.status = "REMEDIATING"
    state.chart_data.pop(0)
    state.chart_data.append({"time": datetime.now().strftime("%H:%M:%S"), "actualCost": 80.0, "projectedCost": 88.0})
    await asyncio.sleep(2.0)
    
    state.status = "HEALTHY"
    new_active = 8 - len(state.offline_nodes) - 1
    drop_cost = 0 if new_active == 0 else (new_active * 1.2)
    
    state.chart_data.pop(0)
    state.chart_data.append({"time": datetime.now().strftime("%H:%M:%S"), "actualCost": round(drop_cost, 2), "projectedCost": 90.0})
    
    state.offline_nodes.append(target_node)
    
    # Output Official AI Result to React
    act_log = {
        "id": int(time.time() * 1000),
        "timestamp": datetime.now().strftime("%I:%M:%S %p"),
        "resourceId": f"i-core-node-{target_node}",
        "reason": f"AI LOG: {ml_reason}",
        "action": action
    }
    state.logs.insert(0, act_log)
    state.savings += round(random.uniform(50.0, 150.0), 2)
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
