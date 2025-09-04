## How It Works

### Project Filtering
1. **Ticket Creation**: When a ticket is created, the system checks:
   - If the team has a configured project domain
   - If not, uses the company's global project domain
   - If no domain is configured, all projects remain available

2. **Ticket Editing**: The project domain is automatically applied to the "Project" field of the ticket

3. **Validation**: If the project domain is invalid, the system ignores it and shows all projects

### Task Filtering
1. **Project Selection**: When a project is selected in a ticket:
   - The system applies the configured task domain
   - Tasks are automatically filtered by the selected project
   - Only tasks belonging to the selected project are shown

2. **Dynamic Filtering**: Task filtering is updated when:
   - The project field changes
   - The team changes
   - Other relevant ticket fields change

3. **Smart Filtering**: The system ensures tasks are always relevant to the selected project, preventing selection of tasks from other projects

### Domain Application
- **Static Domains**: Applied immediately when fields change
- **Python Domains**: Evaluated dynamically based on current ticket data
- **Combination Logic**: All applicable domains are combined using AND logic
- **Fallback Behavior**: If any domain fails, the system gracefully falls back to showing all available options
