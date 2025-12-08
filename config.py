"""
Configuration and constants for MarkPolish Studio
Contains templates, setup constants, and initialization code
"""

import os
import streamlit as st

# Page configuration
PAGE_CONFIG = {
    "page_title": "MarkPolish V1.0",
    "layout": "wide",
    "initial_sidebar_state": "collapsed"
}

# Export individual config values for app.py compatibility
APP_TITLE = PAGE_CONFIG["page_title"]
LAYOUT = PAGE_CONFIG["layout"]
INITIAL_SIDEBAR_STATE = PAGE_CONFIG["initial_sidebar_state"]

# Sidebar hover HTML (for collapsible sidebar)
SIDEBAR_HOVER_HTML = """
<div id="mp-sidebar-wrapper" style="position: fixed; left: 0; top: 0; width: 100px; height: 100vh; z-index: 999999; pointer-events: none;">
    <div id="mp-sidebar-trigger" style="position: absolute; left: 0; top: 0; width: 100px; height: 100vh; pointer-events: auto; background: transparent;"></div>
</div>
<style>
    section[data-testid="stSidebar"] {
        position: fixed !important;
        left: -21rem !important;
        transition: left 0.3s ease !important;
        z-index: 999 !important;
    }
    .main .block-container {
        padding-left: 1rem !important;
    }
</style>
<script>
(function() {
    function ensureTrigger() {
        let trigger = document.getElementById('mp-sidebar-trigger');
        if (!trigger) {
            const wrapper = document.getElementById('mp-sidebar-wrapper');
            if (wrapper) {
                trigger = document.createElement('div');
                trigger.id = 'mp-sidebar-trigger';
                trigger.style.cssText = 'position: absolute; left: 0; top: 0; width: 100px; height: 100vh; pointer-events: auto; background: transparent;';
                wrapper.appendChild(trigger);
            }
        }
        return trigger;
    }
    
    function setupSidebar() {
        const sidebar = document.querySelector('section[data-testid="stSidebar"]');
        const trigger = ensureTrigger();
        
        if (!sidebar || !trigger) {
            setTimeout(setupSidebar, 200);
            return;
        }
        
        let hideTimer = null;
        
        function show() {
            clearTimeout(hideTimer);
            sidebar.style.setProperty('left', '0', 'important');
        }
        
        function hide() {
            clearTimeout(hideTimer);
            hideTimer = setTimeout(function() {
                sidebar.style.setProperty('left', '-21rem', 'important');
            }, 300);
        }
        
        // Remove old listeners
        const newTrigger = trigger.cloneNode(true);
        trigger.parentNode.replaceChild(newTrigger, trigger);
        
        // Trigger events
        newTrigger.addEventListener('mouseenter', show);
        newTrigger.addEventListener('mouseleave', function(e) {
            setTimeout(function() {
                const rect = sidebar.getBoundingClientRect();
                if (e.clientX < rect.right) return;
                hide();
            }, 100);
        });
        
        // Sidebar events
        sidebar.addEventListener('mouseenter', function() {
            clearTimeout(hideTimer);
            show();
        });
        sidebar.addEventListener('mouseleave', function(e) {
            setTimeout(function() {
                const rect = newTrigger.getBoundingClientRect();
                if (e.clientX <= rect.right) return;
                hide();
            }, 100);
        });
        
        // Global mousemove
        document.addEventListener('mousemove', function(e) {
            if (e.clientX <= 100) {
                show();
            }
        }, true);
    }
    
    setupSidebar();
    window.addEventListener('load', setupSidebar);
    setInterval(function() {
        const sidebar = document.querySelector('section[data-testid="stSidebar"]');
        const trigger = document.getElementById('mp-sidebar-trigger');
        if (sidebar && !trigger) {
            ensureTrigger();
            setupSidebar();
        }
    }, 500);
})();
</script>
"""

# Template library
TEMPLATES = {
    "Empty Draft": "",
    
    # === PRODUCT & ANNOUNCEMENTS ===
    "📢 Product Launch": """::: hero
# New Feature: Dark Mode
The feature you asked for is here.
:::

[IMG: app interface dark mode ui ux clean minimal]

## Why This Matters
Users engage 40% more in low-light environments.

::: col-2
**Comfort**
Reduced eye strain.
--split--
**Battery**
Saves energy on OLED.
:::

::: steps
1. Go to Settings
2. Click Appearance
3. Toggle Dark Mode
:::

[Update Now](https://example.com)""",
    
    "🎉 Feature Announcement": """::: hero
# 🎊 Exciting News!
We're thrilled to announce our latest feature
:::

[IMG: modern app feature announcement ui design]

## What's New?

## Key Benefits

::: col-3
**Fast**
Lightning quick performance
--split--
**Secure**
Enterprise-grade security
--split--
**Simple**
Easy to use interface
:::

## How to Get Started

::: steps
1. Sign up for free
2. Explore the new feature
3. Share your feedback
:::

[Try It Now](https://example.com)""",
    
    "📱 App Update": """::: hero
# Version 2.0 is Here!
Major update with new features and improvements
:::

[IMG: mobile app update notification modern design]

## What's Changed

## New Features

## Bug Fixes

## Performance Improvements

[Download Update](https://example.com)""",
    
    # === CONTENT & NEWS ===
    "📰 Weekly Newsletter": """::: hero
# Weekly Insights #42
Trends in AI & Design
:::

## 1. The Big Picture
AI is moving from "Chat" to "Structure".

::: timeline
2023 Chatbots
2024 Agents
2025 Context-Aware OS
:::

## 2. Design Tip
Use whitespace effectively.

[Read Full Story](https://example.com)""",
    
    "📝 Blog Post": """::: hero
# How to Build Better Products
A guide to modern product development
:::

[IMG: modern workspace productivity design]

## Introduction

## Main Content

## Conclusion

[Share This Article](https://example.com)""",
    
    "📊 Industry Report": """::: hero
# 2024 Industry Trends Report
Key insights and predictions
:::

[IMG: data visualization charts graphs analytics]

## Executive Summary

## Key Findings

::: col-2
**Finding 1**
Detailed explanation here
--split--
**Finding 2**
Detailed explanation here
:::

## Recommendations

[Download Full Report](https://example.com)""",
    
    # === MARKETING & PROMOTIONS ===
    "🎯 Promotional Campaign": """::: hero
# Limited Time Offer!
Special discount for early adopters
:::

[IMG: promotional banner modern design sale]

## What You Get

## Why Act Now?

::: steps
1. Limited availability
2. Exclusive pricing
3. Bonus features included
:::

## Pricing

[Claim Your Discount](https://example.com)""",
    
    "💼 Case Study": """::: hero
# Success Story: How Company X Achieved 300% Growth
Real results from real customers
:::

[IMG: business success team collaboration]

## The Challenge

## The Solution

## The Results

::: col-2
**Before**
Baseline metrics
--split--
**After**
Improved metrics
:::

## Key Takeaways

[Read More Case Studies](https://example.com)""",
    
    "🎁 Special Offer": """::: hero
# Exclusive Deal Just for You!
Don't miss this opportunity
:::

[IMG: special offer gift box modern design]

## What's Included

## Limited Time

## How to Redeem

::: steps
1. Click the button below
2. Enter your code
3. Enjoy your benefits
:::

[Redeem Now](https://example.com)""",
    
    # === EDUCATIONAL & TUTORIALS ===
    "📚 Tutorial Guide": """::: hero
# Complete Guide to Getting Started
Step-by-step instructions for beginners
:::

[IMG: tutorial guide learning education]

## Prerequisites

## Step 1: Setup

## Step 2: Configuration

## Step 3: First Steps

::: steps
1. Install the software
2. Create your account
3. Complete the setup wizard
4. Start creating
:::

## Common Questions

[Need Help?](https://example.com)""",
    
    "🎓 How-To Article": """::: hero
# How to Master This Skill
A comprehensive guide for all levels
:::

[IMG: learning skill development tutorial]

## Overview

## Getting Started

## Advanced Techniques

::: col-2
**Beginner Tips**
Start here if you're new
--split--
**Pro Tips**
For experienced users
:::

## Resources

[Explore More Guides](https://example.com)""",
    
    "📖 FAQ Document": """::: hero
# Frequently Asked Questions
Everything you need to know
:::

## General Questions

## Technical Questions

## Billing Questions

## Support Questions

[Contact Support](https://example.com)""",
    
    # === EVENTS & ANNOUNCEMENTS ===
    "🎪 Event Announcement": """::: hero
# Join Us for an Amazing Event!
Save the date and don't miss out
:::

[IMG: event announcement conference meeting]

## Event Details

## What to Expect

::: timeline
9:00 AM Registration
10:00 AM Keynote
11:30 AM Workshops
2:00 PM Networking
:::

## Speakers

## Register Now

[Get Your Ticket](https://example.com)""",
    
    "📅 Webinar Invitation": """::: hero
# Free Webinar: Learn from Experts
Join us for an exclusive online session
:::

[IMG: webinar online meeting presentation]

## What You'll Learn

## Who Should Attend

## Agenda

::: steps
1. Introduction
2. Main presentation
3. Q&A session
4. Next steps
:::

[Register Free](https://example.com)""",
    
    "🎊 Company Milestone": """::: hero
# Celebrating 10 Years of Innovation!
Thank you for being part of our journey
:::

[IMG: celebration milestone achievement]

## Our Journey

::: timeline
2014 Founded
2017 First major product
2020 Global expansion
2024 10 years strong
:::

## Thank You

## What's Next

[Learn More](https://example.com)""",
    
    # === INTERNAL & TEAM ===
    "📋 Meeting Summary": """::: hero
# Team Meeting Summary
Key points and action items
:::

## Attendees

## Discussion Points

## Decisions Made

## Action Items

::: steps
1. Task 1 - Owner: Name - Due: Date
2. Task 2 - Owner: Name - Due: Date
3. Task 3 - Owner: Name - Due: Date
:::

## Next Steps

[View Full Notes](https://example.com)""",
    
    "📢 Internal Announcement": """::: hero
# Important Team Update
Please read and acknowledge
:::

## Overview

## Changes

## Impact

## Timeline

::: timeline
Week 1 Preparation
Week 2 Implementation
Week 3 Review
:::

## Questions?

[Contact HR](https://example.com)""",
    
    "🎯 Project Update": """::: hero
# Project Status Report
Current progress and next steps
:::

[IMG: project management dashboard]

## Current Status

## Completed This Week

## Upcoming Tasks

## Blockers

## Metrics

::: col-2
**Progress**
75% Complete
--split--
**Timeline**
On Track
:::

[View Dashboard](https://example.com)""",
    
    # === CUSTOMER & SUPPORT ===
    "💬 Customer Testimonial": """::: hero
# What Our Customers Say
Real feedback from real users
:::

[IMG: happy customer testimonial review]

## Customer Quote

> "This product has transformed how we work. Highly recommended!"

## Customer Story

## Results Achieved

[Read More Testimonials](https://example.com)""",
    
    "🆘 Support Guide": """::: hero
# Need Help? We're Here for You!
Quick solutions to common issues
:::

[IMG: customer support help center]

## Quick Solutions

## Still Need Help?

::: steps
1. Check our knowledge base
2. Search existing tickets
3. Contact support team
:::

## Contact Options

[Get Support](https://example.com)""",
    
    "🎁 Welcome Message": """::: hero
# Welcome to Our Platform!
We're excited to have you here
:::

[IMG: welcome onboarding new user]

## Getting Started

::: steps
1. Complete your profile
2. Explore the features
3. Join the community
:::

## Resources

## Need Help?

[Start Your Journey](https://example.com)""",
    
    # === SPECIAL FORMATS ===
    "📸 Photo Story": """::: hero
# A Day in the Life
Visual storytelling at its best
:::

[IMG: beautiful landscape photography]

## Scene 1

[IMG: people working together]

## Scene 2

[IMG: sunset evening mood]

## Scene 3

[Share Your Story](https://example.com)""",
    
    "🎬 Video Post": """::: hero
# Watch Our Latest Video
New content just released
:::

[IMG: video thumbnail preview design]

## About This Video

## Key Highlights

## Watch Now

[Play Video](https://example.com)""",
    
    "📊 Data Report": """::: hero
# Monthly Analytics Report
Key metrics and insights
:::

[IMG: analytics dashboard charts data]

## Overview

## Key Metrics

::: col-3
**Users**
10,000+
--split--
**Growth**
25% MoM
--split--
**Engagement**
85% Active
:::

## Trends

## Recommendations

[View Full Report](https://example.com)""",
    
    # === QUICK TEMPLATES ===
    "⚡ Quick Update": """## Quick Update

Brief announcement here.

[Learn More](https://example.com)""",
    
    "📌 Simple Notice": """## Important Notice

Please note the following:

- Point 1
- Point 2
- Point 3

Thank you for your attention.""",
    
    "💡 Tip of the Day": """::: hero
# 💡 Pro Tip
Today's helpful tip
:::

## The Tip

## Why It Works

## Try It Now

[Share This Tip](https://example.com)"""
}


def initialize_directories():
    """Initialize required directories"""
    if not os.path.exists("projects"):
        os.makedirs("projects")
    if not os.path.exists("projects/images"):
        os.makedirs("projects/images")

# Alias for app.py compatibility
setup_directories = initialize_directories


def setup_page_config():
    """Setup Streamlit page configuration"""
    st.set_page_config(**PAGE_CONFIG)


def setup_sidebar_hover():
    """Setup collapsible sidebar with hover functionality"""
    if "sidebar_hover_init" not in st.session_state:
        st.session_state.sidebar_hover_init = True
    st.components.v1.html(SIDEBAR_HOVER_HTML, height=0)

