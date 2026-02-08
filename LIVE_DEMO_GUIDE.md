# 🎯 Live Chatbot Demonstration Guide

## Let's Test Your Chatbot Right Now!

Follow these steps to see your AI chatbot in action:

---

## Step 1: Open Your Todo App

1. Open your web browser
2. Navigate to: **http://localhost:3000**
3. You should see the Todo App login/signup page

---

## Step 2: Sign In or Create Account

**If you have an account:**
- Enter your email and password
- Click "Sign In"

**If you need to create an account:**
- Click "Sign Up"
- Enter your email and password
- Click "Create Account"

---

## Step 3: Locate the Chat Button

Once you're on the Tasks page, look at the **top-right corner** of the navigation bar.

You should see:
```
[💬 Show AI Chat] [your-email@example.com] [Logout]
```

The chat button is **blue** with a chat bubble icon.

---

## Step 4: Open the Chat Panel

1. Click the **"Show AI Chat"** button
2. The page layout will change:
   - Tasks section moves to the left (2/3 width)
   - Chat panel appears on the right (1/3 width)
3. You'll see the chat interface with:
   - Header: "AI Task Assistant"
   - Empty message area (if first time)
   - Input field at the bottom

---

## Step 5: Send Your First Message

**Test 1: Create a Task**

Type in the chat input:
```
Add a task to buy groceries
```

Press **Enter** or click the **send button** (paper plane icon)

**What should happen:**
1. Your message appears in a blue bubble on the right
2. Loading animation (three bouncing dots)
3. AI response appears in a gray bubble on the left
4. "Actions taken: • add_task" shown below the response
5. **Task list on the left automatically updates** with the new task!

---

## Step 6: Try More Commands

**Test 2: List Your Tasks**

Type:
```
Show my tasks
```

**Expected result:**
- AI lists all your tasks in the chat
- Shows task details (title, priority, status)

---

**Test 3: Create a High Priority Task**

Type:
```
Create a high priority task to finish the report by Friday
```

**Expected result:**
- AI confirms task creation
- New task appears in the task list with HIGH priority
- Task list refreshes automatically

---

**Test 4: View Conversation History**

Type:
```
What tasks did I just create?
```

**Expected result:**
- AI remembers previous conversation
- References the tasks you created earlier
- Shows context awareness

---

## Step 7: Verify Real-time Updates

1. Create a task via chat: `"Add task: Call dentist"`
2. **Watch the task list on the left** - it should update immediately
3. The new task appears without refreshing the page
4. This confirms the real-time integration is working!

---

## Step 8: Test the Toggle

1. Click **"Hide AI Chat"** button
2. Chat panel disappears
3. Task list expands to full width
4. Click **"Show AI Chat"** again
5. Chat panel reappears with your conversation history intact

---

## 🎨 Visual Guide

```
┌─────────────────────────────────────────────────────────────┐
│  Todo App                    [💬 Show AI Chat] [Logout]     │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────────────┐  ┌──────────────────────────────┐ │
│  │   TASKS (2/3)       │  │   AI CHAT (1/3)              │ │
│  │                     │  │                               │ │
│  │  Create Task Form   │  │  ┌────────────────────────┐  │ │
│  │  ┌────────────────┐ │  │  │ AI Task Assistant      │  │ │
│  │  │ Title: _______ │ │  │  └────────────────────────┘  │ │
│  │  │ Priority: [v]  │ │  │                               │ │
│  │  └────────────────┘ │  │  [User] Add task to buy...   │ │
│  │                     │  │                               │ │
│  │  Task List          │  │  [AI] I'll add that task...  │ │
│  │  ☐ Buy groceries    │  │  Actions: • add_task         │ │
│  │  ☐ Call dentist     │  │                               │ │
│  │  ☐ Finish report    │  │  [User] Show my tasks        │ │
│  │                     │  │                               │ │
│  │                     │  │  [AI] Here are your tasks... │ │
│  │                     │  │                               │ │
│  │                     │  │  ┌────────────────────────┐  │ │
│  │                     │  │  │ Type message...        │  │ │
│  │                     │  │  └────────────────────────┘  │ │
│  └─────────────────────┘  └──────────────────────────────┘ │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## ✅ Success Indicators

Your chatbot is working correctly if you see:

1. ✅ Chat panel appears when you click "Show AI Chat"
2. ✅ Messages send when you press Enter
3. ✅ AI responds within 1-2 seconds
4. ✅ "Actions taken" appears for task operations
5. ✅ Task list updates automatically
6. ✅ Conversation history is maintained
7. ✅ Chat panel can be hidden/shown without losing history

---

## 🐛 Troubleshooting

### Chat button not visible?
- **Solution**: Refresh the page (F5 or Ctrl+R)
- Make sure you're signed in
- Check you're on the `/tasks` page

### Messages not sending?
- **Check**: Open browser console (F12)
- Look for any red error messages
- Verify backend is running: http://localhost:8000/health

### AI not responding?
- **Check**: Network tab in browser dev tools (F12)
- Look for failed API calls
- Verify authentication token is valid

### Tasks not updating?
- **Check**: Console for errors
- Verify the `onTaskUpdate` callback is firing
- Check if MCP tools are executing successfully

---

## 📸 Screenshot Checklist

Take screenshots at these points to verify everything works:

1. [ ] Tasks page with "Show AI Chat" button visible
2. [ ] Chat panel open with empty state
3. [ ] First message sent and AI response received
4. [ ] Task list showing newly created task
5. [ ] "Actions taken" indicator visible
6. [ ] Multiple messages in conversation
7. [ ] Chat panel hidden (full-width tasks)

---

## 🎉 Congratulations!

If you've completed all these steps successfully, your AI chatbot is fully functional!

You now have:
- ✅ Natural language task management
- ✅ Real-time task updates
- ✅ Conversation history
- ✅ Responsive design
- ✅ Secure authentication

**Enjoy your AI-powered todo app!** 🚀

---

## 📝 Next: Share Your Experience

Try these advanced commands:
- "Create 3 tasks: buy milk, call mom, and finish homework"
- "Show only high priority tasks"
- "What's my most urgent task?"
- "Help me organize my day"

The chatbot will do its best to understand and help you!
