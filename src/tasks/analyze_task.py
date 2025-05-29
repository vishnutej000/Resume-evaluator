class AnalyzeTask:
    def __init__(self, agent, description="Analyze GitHub profiles and calculate final scores"):
        self.agent = agent
        self.description = description

    def execute(self, candidates):
        """Execute the analyze task"""
        return self.agent.enrich_candidates(candidates)