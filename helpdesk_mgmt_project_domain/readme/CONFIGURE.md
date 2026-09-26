To configure this module, you need to:

1. Configure global project and task domains at company level.
2. Configure team-specific project and task domains.
3. Set up Python-based dynamic domains (optional).

## Global Configuration (Company)

1. Go to **Settings > Helpdesk** to configure the global project and task domains.
2. In the "Project & Task Domain Configuration" section, set the **Project Domain** field using the visual domain builder.
3. Set the **Task Domain** field using the visual domain builder.
4. These domains will be applied to all teams that don't have their own domains configured.
5. You can also Activate or Deactivate the global domains.

## Team Configuration

1. Go to **Helpdesk > Configuration > Teams** to configure team-specific domains.
2. Edit or create a team.
3. In the **Project Domain** tab:
   - Set the **Project Domain** field using the visual domain builder.
   - Configure the **Project Domain Python Code** field for dynamic domains (optional).
4. In the **Task Domain** tab:
   - Set the **Task Domain** field using the visual domain builder.
   - Configure the **Task Domain Python Code** field for dynamic domains (optional).
5. Team domains will be combined with the company domain using AND logic.

## Domain Builder Usage

Both "Project Domain" and "Task Domain" fields use a visual builder that allows:

1. **Click on the field** to open the domain builder.
2. **Select the field** from the Project/Task model (e.g., Active, Partner, Type, User).
3. **Choose the operator** (e.g., =, !=, >, <, in, not in).
4. **Define the value** (e.g., True, False, partner name, user name).
5. **Add more conditions** with AND/OR logic.
6. **Save** the domain configuration.

## Domain Examples

### Project Domain Examples

#### Only Active Projects
- Field: Active
- Operator: =
- Value: True
- Domain: `[('active', '=', True)]`

#### Projects with Partner
- Field: Partner
- Operator: !=
- Value: False
- Domain: `[('partner_id', '!=', False)]`

#### Projects from Specific Client
- Field: Partner
- Operator: =
- Value: [Client Name]
- Domain: `[('partner_id', '=', 123)]` (where 123 is the client ID)

#### Projects by Tags (Internal Projects)
- Field: Tags
- Operator: in
- Value: [Internal]
- Domain: `[('tag_ids', 'in', [4])]` (where 4 is the tag ID)

#### Projects by Tags (External Projects)
- Field: Tags
- Operator: in
- Value: [External]
- Domain: `[('tag_ids', 'in', [5])]` (where 5 is the tag ID)

#### Mixed Project Tags (Internal OR External)
- Field: Tags
- Operator: in
- Value: [Internal, External]
- Domain: `['|', ('tag_ids', 'in', [4]), ('tag_ids', 'in', [5])]`

### Task Domain Examples

#### Only Active Tasks
- Field: Active
- Operator: =
- Value: True
- Domain: `[('active', '=', True)]`

#### Tasks by Tags (Development)
- Field: Tags
- Operator: in
- Value: [Development]
- Domain: `[('tag_ids', 'in', [1])]` (where 1 is the tag ID)

#### Tasks by Tags (Testing)
- Field: Tags
- Operator: in
- Value: [Testing]
- Domain: `[('tag_ids', 'in', [2])]` (where 2 is the tag ID)

#### Mixed Task Tags (Development OR Testing)
- Field: Tags
- Operator: in
- Value: [Development, Testing]
- Domain: `['|', ('tag_ids', 'in', [1]), ('tag_ids', 'in', [2])]`

#### Unassigned Tasks
- Field: User
- Operator: =
- Value: False
- Domain: `[('user_ids', '=', False)]`

#### Tasks Assigned to Specific User
- Field: User
- Operator: in
- Value: [User Name]
- Domain: `[('user_ids', 'in', [123])]` (where 123 is the user ID)

#### Tasks with High Priority
- Field: Priority
- Operator: =
- Value: 1
- Domain: `[('priority', '=', '1')]`

## Python Domain Code

For advanced users, you can use Python code to create dynamic domains:

1. Go to the team configuration.
2. Edit the **Project Domain Python Code** or **Task Domain Python Code** field.
3. Write Python code that returns a domain list.
4. Available variables: ticket, env, user, company, AND, OR, normalize.

### Example Python Code

#### Project Domain Example - Client Projects Team
```python
# Filter projects based on ticket partner (from demo data)
if ticket.partner_id:
    domain = [('commercial_partner_id', '=', ticket.commercial_partner_id.id)]
else:
    domain = [('id', '=', 0)]  # No projects if no partner
```

#### Task Domain Example - Unassigned Tasks
```python
# Filter tasks not assigned to anyone (from demo data)
domain = [('user_ids', '=', False)]
```

#### Task Domain Example - Project-based Filtering
```python
# Filter tasks based on ticket project
if ticket.project_id:
    domain = [('project_id', '=', ticket.project_id.id)]
else:
    domain = [('id', '=', 0)]  # No tasks if no project selected
```

#### Task Domain Example - Mixed Tags
```python
# Filter tasks by development or testing tags (from demo data)
domain = ['|', ('tag_ids', 'in', [1]), ('tag_ids', 'in', [2])]
```

#### Task Domain Example - Priority and Assignment
```python
# Filter high priority tasks assigned to specific users
if ticket.partner_id:
    domain = AND([
        [('priority', '=', '1')],  # High priority
        [('user_ids', '!=', False)]  # Assigned tasks
    ])
else:
    domain = [('priority', '=', '1')]  # High priority only
```

## Domain Combination Logic

All domains are combined using AND logic:

### For Projects:
1. **Company global project domain** (base filter for all teams).
2. **Team static project domain** (always combined with company domain).
3. **Team Python project code** (always combined with company + team domains).

### For Tasks:
1. **Company global task domain** (base filter for all teams).
2. **Team static task domain** (always combined with company domain).
3. **Team Python task code** (always combined with company + team domains).

The final project domain will be: Company Project Domain AND Team Project Domain AND Python Project Domain.

The final task domain will be: Company Task Domain AND Team Task Domain AND Python Task Domain.


## Permissions

There are no specific permissions required for this module. The domain filtering
respects the user's existing project access permissions set in the system.

## Troubleshooting

If domains are not working as expected:

1. Check that the domain syntax is correct.
2. Verify that the Python code (if used) has no syntax errors.
3. Ensure that the fields referenced in domains exist in the Project model.
4. Check the Odoo logs for any domain evaluation errors.
