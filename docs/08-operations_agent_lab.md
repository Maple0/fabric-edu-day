# Hands-On Lab: Operations Agent

Create a Fabric Operations Agent that monitors real-time student attendance data in the university eventhouse and sends an alert via Microsoft Teams when a student is absent.

---

## Prerequisites

- Fabric workspace with a Microsoft Fabric-enabled capacity (trial capacities are not supported)
- Eventhouse `university_database` created with a KQL database containing the `fact_attendance` table
- The `fact_attendance` table includes an `is_present` column (0 = absent, 1 = present)
- Microsoft Teams account
- Tenant admin has enabled:
  - **Operations Agent (preview)** in Fabric tenant settings
  - **Copilot and Azure OpenAI Service**
- If your Fabric capacity is not in US or EU regions, enable **cross-geo processing and storage for AI** under Data Agent tenant settings

---

## Step 1: Create the Operations Agent

1. In the Fabric home page, click the ellipsis **...** icon, then select **Create**
2. In the **Create** pane, go to the **Real-Time Intelligence** section and select **Operations Agent**
3. In the **Create operations agent** pane:
   - Name: `University Attendance Monitor`
   - Workspace: select your **My Workspace**
4. Click **Create**

---

## Step 2: Configure Business Goals

1. In the **Agent setup** page, locate the **Business goals** section
2. Enter the following business goal:

```
Monitor student attendance in real time. Identify students who are absent from their scheduled classes so that academic staff can follow up promptly. The goal is to reduce unexcused absences and ensure student welfare.
```

---

## Step 3: Provide Agent Instructions

1. In the **Agent instructions** section, enter the following:

```
You are an attendance monitoring agent for a Singapore university.

Monitor the fact_attendance table in the University KQL database within the university_database eventhouse.

A student is considered absent when the is_present column equals 0.

When you detect an absent student (is_present = 0), raise an alert immediately. Include the following details in the alert:
- Student key (student_key)
- Course key (course_key)
- Date of absence (date_key)
- Any other relevant context from the attendance record

Do not alert for students who are present (is_present = 1).
```

---

## Step 4: Connect the Knowledge Source

1. In the **Knowledge source** section, click **Add knowledge source**
2. Select the eventhouse `university_database` as the data source
3. Select the KQL database that contains the `fact_attendance` table
4. Confirm the connection and ensure the agent can access the `fact_attendance` table

---

## Step 5: Define the Alert Action

1. In the **Actions** section, click **Add action**
2. Configure the action:
   - Action name: `Send Absence Alert`
   - Description: `Send an alert notification via Teams when a student is marked absent`
   - Parameters (optional): `student_key`, `course_key`, `date_key`
3. After creating the action, click on it to configure:
   1. In the **Configure custom action** pane, select your workspace and the activator item
   2. Create a connection
   3. Copy the **Connection string** and click **Open flow builder**
   4. In the **Flow builder**, paste the connection string in the **Connection string** field
   5. Configure the flow to send a Teams message with the absence details
   6. Click **Save**

---

## Step 6: Save and Review the Playbook

1. Click **Save** to generate the agent's playbook
2. Review the playbook to confirm:
   - The agent monitors the `fact_attendance` table
   - The rule triggers when `is_present = 0`
   - The action sends a Teams notification with student and course details
3. If the playbook does not match your requirements, update the business goals or instructions and save again

---

## Step 7: Start the Agent

1. Click **Start** in the toolbar to activate the agent
2. The agent will now continuously monitor the `fact_attendance` table for absent students

---

## Step 8: Install the Teams App and Verify Alerts

1. Open Microsoft Teams
2. Search for **Fabric Operations Agent** in the Teams app store and install it
3. Once installed, the agent will send you messages in Teams when it detects a student absence (`is_present = 0`)
4. Each alert message includes:
   - A summary of the absence data that triggered the alert
   - Recommended actions
5. Select **Yes** to approve or **No** to reject the recommended action
6. To update who receives alert messages, go to the operations agent item settings in Fabric under **Agent behavior**

> **Note:** The agent operates using the delegated identity and permissions of its creator. When a recipient approves a recommendation, the agent executes the action on behalf of the creator.

---

## Step 9: Stop the Agent

1. When testing is complete, click **Stop** in the toolbar to deactivate the agent
2. You can restart it at any time by clicking **Start** again

---

## Validation Checklist

- [ ] Operations Agent `University Attendance Monitor` created in My Workspace
- [ ] Knowledge source connected to the `university_database` eventhouse and `fact_attendance` table
- [ ] Business goals and agent instructions configured for absence monitoring
- [ ] Alert action configured to send Teams notifications when `is_present = 0`
- [ ] Agent started and playbook reviewed
- [ ] Fabric Operations Agent Teams app installed and alert messages received
