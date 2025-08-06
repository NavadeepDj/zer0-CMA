# JotForm Chatbot Setup Guide

This guide provides step-by-step instructions for setting up the JotForm chatbot interface for the Complaint Management System.

## Prerequisites

1. JotForm account (free or paid)
2. Access to JotForm's chatbot/conversational form features
3. Webhook endpoint URL (will be provided by Flask backend)

## Setup Instructions

### Step 1: Create JotForm Account and Access Chatbot Features

1. Go to https://www.jotform.com and create an account
2. Navigate to "Create Form" → "Conversational Forms" or "Chatbot"
3. Select "Customer Support" template if available, or start with blank conversational form

### Step 2: Configure Basic Chatbot Structure

1. Set up the welcome message and initial options
2. Configure the multi-step conversation flow
3. Add conditional logic for different user paths
4. Set up webhook integration for data submission

### Step 3: Test and Deploy

1. Test all conversation flows
2. Verify webhook integration
3. Deploy the chatbot and get the public URL

## Form Configuration Details

See the `chatbot-config.json` file for the complete form structure and logic configuration.