class ParseTask:
    def __init__(self, agent, description="Parse and evaluate resume content"):
        self.agent = agent
        self.description = description

    def execute(self, attachments):
        """Execute the parse task and return detailed parsing results for each attachment."""
        results = []
        for attachment in attachments:
            result = self.agent.evaluate_candidates([attachment])
            if result:
                results.extend(result)
            else:
                results.append({'filename': attachment.get('filename', 'unknown'), 'error': 'Parsing failed'})
        return results