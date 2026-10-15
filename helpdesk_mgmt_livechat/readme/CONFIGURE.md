This module does not require additional configuration after installation. It works automatically once installed.

## Installation

1. Go to the **Apps** menu
2. Remove the "Apps" filter if necessary
3. Search for "Helpdesk Management Livechat"
4. Click **Install**

The module will be automatically installed when both `helpdesk_mgmt` and `im_livechat` are installed.

## Prerequisites

Make sure the following modules are installed:
* **Helpdesk Management** (base helpdesk module)
* **Livechat** (Odoo's livechat module)

The system will automatically install the necessary dependencies during installation.

## Configuration

**Setting up Chatbot Ticket Creation**

1. Go to **Settings > Livechat > Chatbots**
2. Create or edit a chatbot script
3. Add steps to your chatbot workflow
4. Add a step with type **"Create Ticket"**
5. Configure the step:
   * Select a **Helpdesk Team** (optional)
   * The ticket will be assigned to this team when created
6. Save the chatbot script

**Using the /ticket Command**

No additional configuration is required. The `/ticket` command is automatically available in all livechat conversations.

## Permissions

The module uses the same access permissions as the base modules:
* Users with access to **Helpdesk** can view tickets created from livechat
* Users with access to **Livechat** can use the `/ticket` command
* Users with access to **Chatbots** can configure chatbot ticket creation

No additional permission configuration is required.

## Channel Setup

The module automatically creates a "Livechat" channel in the helpdesk system. This channel is used to track all tickets created from livechat conversations.

If the channel doesn't exist, it will be created automatically when the first ticket is created.

