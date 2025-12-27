"""
Script to create sample data for testing the HR Onboarding System
"""
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import AsyncSessionLocal
from app.models import (
    UserModel, TaskModel, TrainingModuleModel, 
    EmployeeTaskModel, EmployeeTrainingModel
)
from app.core.enums import UserRole, TaskType, DocumentType
from app.auth import get_password_hash


async def create_sample_data():
    """Create sample users, tasks, and training modules"""
    async with AsyncSessionLocal() as session:
        # Create HR user
        hr_user = UserModel(
            name="John HR",
            email="john.hr@company.com",
            password_hash=get_password_hash("password123"),
            role=UserRole.HR
        )
        session.add(hr_user)
        await session.commit()
        await session.refresh(hr_user)
        
        # Create Employee users
        employees = [
            UserModel(
                name="Jane Employee",
                email="jane.employee@company.com",
                password_hash=get_password_hash("password123"),
                role=UserRole.EMPLOYEE
            ),
            UserModel(
                name="Bob Employee",
                email="bob.employee@company.com",
                password_hash=get_password_hash("password123"),
                role=UserRole.EMPLOYEE
            ),
            UserModel(
                name="Alice Employee",
                email="alice.employee@company.com",
                password_hash=get_password_hash("password123"),
                role=UserRole.EMPLOYEE
            )
        ]
        
        for employee in employees:
            session.add(employee)
        await session.commit()
        
        for employee in employees:
            await session.refresh(employee)
        
        # Create sample tasks
        tasks = [
            TaskModel(
                title="Read Company Policy",
                description="Please read and understand our company policies and code of conduct",
                task_type=TaskType.READ,
                content="""
                # Company Policy and Code of Conduct
                
                ## 1. Professional Behavior
                - Maintain professional conduct at all times
                - Respect colleagues and clients
                - Follow company dress code
                
                ## 2. Confidentiality
                - Protect company and client information
                - Do not share sensitive data
                - Use secure communication channels
                
                ## 3. Work Hours
                - Standard work hours: 9 AM - 6 PM
                - Flexible working arrangements available
                - Report absences in advance
                
                ## 4. IT Security
                - Use strong passwords
                - Do not share login credentials
                - Report security incidents immediately
                """,
                created_by=hr_user.id
            ),
            TaskModel(
                title="Upload Aadhar Card",
                description="Please upload a clear copy of your Aadhar card for identity verification",
                task_type=TaskType.UPLOAD,
                required_document_type=DocumentType.AADHAR,
                created_by=hr_user.id
            ),
            TaskModel(
                title="Upload Resume",
                description="Please upload your latest resume",
                task_type=TaskType.UPLOAD,
                required_document_type=DocumentType.RESUME,
                created_by=hr_user.id
            ),
            TaskModel(
                title="Sign Employment Agreement",
                description="Please review and sign the employment agreement",
                task_type=TaskType.SIGN,
                content="""
                # Employment Agreement
                
                This agreement is between [Company Name] and the employee.
                
                ## Terms and Conditions:
                1. Employment is at-will
                2. Confidentiality must be maintained
                3. Intellectual property belongs to the company
                4. 30-day notice period for resignation
                
                By completing this task, you agree to the terms above.
                """,
                created_by=hr_user.id
            )
        ]
        
        for task in tasks:
            session.add(task)
        await session.commit()
        
        for task in tasks:
            await session.refresh(task)
        
        # Create training modules
        training_modules = [
            TrainingModuleModel(
                title="Workplace Safety",
                description="Essential workplace safety guidelines and emergency procedures",
                content="""
                # Workplace Safety Training
                
                ## Emergency Procedures
                - Fire evacuation routes
                - Emergency contact numbers
                - First aid procedures
                
                ## General Safety
                - Keep workspaces clean
                - Report hazards immediately
                - Use equipment properly
                
                ## Health Guidelines
                - Ergonomic workspace setup
                - Regular breaks
                - Proper lighting
                """,
                duration_minutes=30,
                is_mandatory=True,
                created_by=hr_user.id
            ),
            TrainingModuleModel(
                title="Company Culture and Values",
                description="Understanding our company mission, vision, and core values",
                content="""
                # Company Culture and Values
                
                ## Our Mission
                To provide excellent service while maintaining the highest standards of integrity.
                
                ## Our Values
                - **Integrity**: We do the right thing, always
                - **Excellence**: We strive for the best in everything we do
                - **Collaboration**: We work together to achieve common goals
                - **Innovation**: We embrace change and new ideas
                
                ## Work Environment
                - Open communication
                - Continuous learning
                - Work-life balance
                - Diversity and inclusion
                """,
                duration_minutes=45,
                is_mandatory=True,
                created_by=hr_user.id
            ),
            TrainingModuleModel(
                title="IT Security Awareness",
                description="Cybersecurity best practices and company IT policies",
                content="""
                # IT Security Awareness
                
                ## Password Security
                - Use strong, unique passwords
                - Enable two-factor authentication
                - Never share credentials
                
                ## Email Security
                - Identify phishing attempts
                - Verify sender identity
                - Report suspicious emails
                
                ## Data Protection
                - Classify data properly
                - Use approved storage solutions
                - Follow data retention policies
                """,
                duration_minutes=60,
                is_mandatory=False,
                created_by=hr_user.id
            )
        ]
        
        for module in training_modules:
            session.add(module)
        await session.commit()
        
        for module in training_modules:
            await session.refresh(module)
        
        # Assign tasks to employees
        for employee in employees:
            for task in tasks:
                assignment = EmployeeTaskModel(
                    employee_id=employee.id,
                    task_id=task.id,
                    assigned_by=hr_user.id
                )
                session.add(assignment)
        
        # Assign training modules to employees
        for employee in employees:
            for module in training_modules:
                training_assignment = EmployeeTrainingModel(
                    employee_id=employee.id,
                    training_module_id=module.id
                )
                session.add(training_assignment)
        
        await session.commit()
        
        print("Sample data created successfully!")
        print("\nLogin credentials:")
        print("HR User: john.hr@company.com / password123")
        print("Employees:")
        for employee in employees:
            print(f"  {employee.email} / password123")


if __name__ == "__main__":
    asyncio.run(create_sample_data())