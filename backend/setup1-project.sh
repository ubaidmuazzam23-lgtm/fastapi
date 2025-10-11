#!/bin/bash

echo "🚀 Creating Job Management Platform Structure..."

# Create main project directory
mkdir -p job-management-platform && cd job-management-platform

# Create root files
touch package.json .gitignore README.md

# Create server structure
mkdir -p server/{src/{controllers,models,routes,middleware,services,utils,sockets,config},logs}
touch server/{package.json,.env,server.js}

# Server source files
touch server/src/controllers/{authController.js,jobController.js,workerController.js,employerController.js,attendanceController.js,chatController.js,analyticsController.js}

touch server/src/models/{User.js,Job.js,Application.js,Attendance.js,Message.js}

touch server/src/routes/{auth.js,jobs.js,workers.js,employers.js,attendance.js,chat.js,analytics.js}

touch server/src/middleware/{auth.js,errorHandler.js,validation.js,rateLimiter.js,cors.js}

touch server/src/services/{jobService.js,workerService.js,attendanceService.js,notificationService.js,emailService.js,analyticsService.js}

touch server/src/utils/{database.js,logger.js,helpers.js,constants.js}

touch server/src/sockets/{index.js,chatHandler.js,notificationHandler.js,attendanceHandler.js}

touch server/src/config/{database.js,clerk.js,aws.js}

# Create client structure
mkdir -p client/{src/{components/{common,worker,employer,admin,chat},pages/{auth,worker,employer,admin},hooks,store/slices,services,utils,styles},public}

touch client/{package.json,.env,vite.config.js,tailwind.config.js,postcss.config.js}

# Client public files
touch client/public/{index.html,favicon.ico,manifest.json}

# Client source files
touch client/src/{main.jsx,App.jsx,index.css}

# Components
touch client/src/components/common/{Header.jsx,Sidebar.jsx,LoadingSpinner.jsx,Modal.jsx,ProtectedRoute.jsx}

touch client/src/components/worker/{JobCard.jsx,AttendanceForm.jsx,ProfileSettings.jsx}

touch client/src/components/employer/{JobPostForm.jsx,WorkerList.jsx,AnalyticsDashboard.jsx}

touch client/src/components/admin/{UserManagement.jsx,SystemSettings.jsx}

touch client/src/components/chat/{ChatWindow.jsx,MessageInput.jsx,UserList.jsx}

# Pages
touch client/src/pages/auth/{Login.jsx,Register.jsx,RoleSelection.jsx}

touch client/src/pages/worker/{WorkerDashboard.jsx,JobBrowse.jsx,MyJobs.jsx,Attendance.jsx,Profile.jsx}

touch client/src/pages/employer/{EmployerDashboard.jsx,JobManagement.jsx,WorkerManagement.jsx,Analytics.jsx,Payroll.jsx}

touch client/src/pages/admin/{AdminDashboard.jsx,UserManagement.jsx,SystemSettings.jsx}

# Hooks and services
touch client/src/hooks/{useSocket.js,useGeolocation.js,useLocalStorage.js}

touch client/src/store/{index.js,middleware.js}
touch client/src/store/slices/{authSlice.js,jobSlice.js,workerSlice.js,chatSlice.js,attendanceSlice.js}

touch client/src/services/{api.js,jobService.js,workerService.js,attendanceService.js,chatService.js}

touch client/src/utils/{constants.js,helpers.js,validators.js}

touch client/src/styles/{globals.css,components.css}

# Create shared directory
mkdir -p shared/{constants,types,utils}
touch shared/constants/{jobTypes.js,userRoles.js,statusCodes.js}
touch shared/types/index.js
touch shared/utils/validation.js

# Create docker directory
mkdir -p docker
touch docker/{Dockerfile.client,Dockerfile.server,docker-compose.yml}

# Create docs directory
mkdir -p docs
touch docs/{API.md,DEPLOYMENT.md,FEATURES.md}

echo "✅ Project structure created successfully!"
echo ""
echo "📁 Directory structure:"
echo "job-management-platform/"
echo "├── 📂 server/ (Node.js Backend)"
echo "│   ├── 📂 src/"
echo "│   │   ├── 📂 controllers/ (7 files)"
echo "│   │   ├── 📂 models/ (5 files)"
echo "│   │   ├── 📂 routes/ (7 files)"
echo "│   │   ├── 📂 middleware/ (5 files)"
echo "│   │   ├── 📂 services/ (6 files)"
echo "│   │   ├── 📂 utils/ (4 files)"
echo "│   │   ├── 📂 sockets/ (4 files)"
echo "│   │   └── 📂 config/ (3 files)"
echo "│   ├── package.json"
echo "│   ├── .env"
echo "│   └── server.js"
echo "├── 📂 client/ (React Frontend)"
echo "│   ├── 📂 src/"
echo "│   │   ├── 📂 components/ (15 files)"
echo "│   │   ├── 📂 pages/ (13 files)"
echo "│   │   ├── 📂 hooks/ (3 files)"
echo "│   │   ├── 📂 store/ (7 files)"
echo "│   │   ├── 📂 services/ (5 files)"
echo "│   │   └── 📂 utils/ (3 files)"
echo "│   ├── package.json"
echo "│   ├── vite.config.js"
echo "│   └── tailwind.config.js"
echo "├── 📂 shared/ (Common utilities)"
echo "├── 📂 docker/ (Docker configuration)"
echo "├── 📂 docs/ (Documentation)"
echo "└── package.json"
echo ""
echo "🔧 Next steps:"
echo "1. cd job-management-platform"
echo "2. Fill in the configuration files (.env, package.json)"
echo "3. npm run install:all"
echo "4. npm run dev"
echo ""
echo "📝 Key features included:"
echo "• Multi-role authentication (Worker/Employer/Admin)"
echo "• Real-time chat with TCP/UDP protocols"
echo "• GPS-based attendance tracking"
echo "• Job management and applications"
echo "• Analytics dashboard"
echo "• Socket.io for real-time communication"
echo "• MongoDB with Mongoose"
echo "• Clerk authentication"
echo "• Tailwind CSS styling"
echo "• Redux state management"
