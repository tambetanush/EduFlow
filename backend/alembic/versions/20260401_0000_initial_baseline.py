"""initial baseline

Revision ID: 20260401_0000
Revises:
Create Date: 2026-04-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20260401_0000'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Users first (no institution_id FK yet — institutions doesn't exist yet)
    user_role_enum = sa.Enum('ADMIN', 'INSTITUTION_ADMIN', 'EDUCATOR', 'STUDENT', 'TECHNICAL_SUPPORT', name='userrole')
    op.create_table(
        'users',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('email', sa.String(), nullable=True),
        sa.Column('password', sa.String(), nullable=True),
        sa.Column('role', user_role_enum, nullable=True),
        sa.Column('institution_id', sa.String(), nullable=True),
        sa.Column('phone', sa.String(), nullable=True),
        sa.Column('profile_photo', sa.String(), nullable=True),
        sa.Column('bio', sa.Text(), nullable=True),
        sa.Column('department', sa.String(), nullable=True),
        sa.Column('parent_name', sa.String(), nullable=True),
        sa.Column('parent_email', sa.String(), nullable=True),
        sa.Column('institution_admin_name', sa.String(), nullable=True),
        sa.Column('institution_admin_address', sa.Text(), nullable=True),
        sa.Column('institution_admin_code', sa.String(), nullable=True),
        sa.Column('theme', sa.String(), server_default='light', nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

    # 2. Institutions (can now FK to users)
    op.create_table(
        'institutions',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('admin_id', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['admin_id'], ['users.id'], name='fk_institution_admin_id'),
        sa.PrimaryKeyConstraint('id')
    )

    # 3. Now add institution_id FK to users (both tables exist now)
    with op.batch_alter_table('users') as batch_op:
        batch_op.create_foreign_key(
            'fk_users_institution_id',
            'institutions',
            ['institution_id'], ['id']
        )

    # 4. Workshops
    op.create_table(
        'workshops',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('start_date', sa.DateTime(), nullable=True),
        sa.Column('end_date', sa.DateTime(), nullable=True),
        sa.Column('institution_id', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['institution_id'], ['institutions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # 5. Modules
    op.create_table(
        'modules',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('workshop_id', sa.String(), nullable=True),
        sa.Column('title', sa.String(), nullable=True),
        sa.Column('order_index', sa.Integer(), nullable=True),
        sa.Column('materials', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['workshop_id'], ['workshops.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # 6. Enrollments
    enrollment_status_enum = sa.Enum('ACTIVE', 'COMPLETED', 'DROPPED', name='enrollmentstatus')
    op.create_table(
        'enrollments',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('student_id', sa.String(), nullable=True),
        sa.Column('workshop_id', sa.String(), nullable=True),
        sa.Column('status', enrollment_status_enum, nullable=True),
        sa.Column('enrolled_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(['student_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['workshop_id'], ['workshops.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # 7. Sessions
    op.create_table(
        'sessions',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('workshop_id', sa.String(), nullable=True),
        sa.Column('title', sa.String(), nullable=True),
        sa.Column('start_time', sa.DateTime(), nullable=True),
        sa.Column('end_time', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['workshop_id'], ['workshops.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # 8. Attendance
    op.create_table(
        'attendance',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('session_id', sa.String(), nullable=True),
        sa.Column('student_id', sa.String(), nullable=True),
        sa.Column('status', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['session_id'], ['sessions.id'], ),
        sa.ForeignKeyConstraint(['student_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # 9. Assessments
    op.create_table(
        'assessments',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('workshop_id', sa.String(), nullable=True),
        sa.Column('module_id', sa.String(), nullable=True),
        sa.Column('title', sa.String(), nullable=True),
        sa.Column('total_marks', sa.Integer(), nullable=True),
        sa.Column('pass_mark', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['module_id'], ['modules.id'], ),
        sa.ForeignKeyConstraint(['workshop_id'], ['workshops.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # 10. Questions
    question_type_enum = sa.Enum('MCQ', 'MSQ', name='questiontype')
    op.create_table(
        'questions',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('assessment_id', sa.String(), nullable=True),
        sa.Column('text', sa.Text(), nullable=True),
        sa.Column('type', question_type_enum, nullable=True),
        sa.Column('marks', sa.Integer(), nullable=True),
        sa.Column('options', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['assessment_id'], ['assessments.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # 11. Submissions
    op.create_table(
        'submissions',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('student_id', sa.String(), nullable=True),
        sa.Column('assessment_id', sa.String(), nullable=True),
        sa.Column('score', sa.Integer(), nullable=True),
        sa.Column('percentage', sa.Integer(), nullable=True),
        sa.Column('pass_fail', sa.Boolean(), nullable=True),
        sa.Column('answers', sa.JSON(), nullable=True),
        sa.Column('submitted_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(['assessment_id'], ['assessments.id'], ),
        sa.ForeignKeyConstraint(['student_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # 12. Certificates
    op.create_table(
        'certificates',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('student_id', sa.String(), nullable=True),
        sa.Column('workshop_id', sa.String(), nullable=True),
        sa.Column('issue_date', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column('verification_code', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['student_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['workshop_id'], ['workshops.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('verification_code')
    )

    # 13. Fee Plans
    op.create_table(
        'fee_plans',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('amount', sa.Integer(), nullable=True),
        sa.Column('billing_cycle', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # 14. Student Fees
    op.create_table(
        'student_fees',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('student_id', sa.String(), nullable=True),
        sa.Column('fee_plan_id', sa.String(), nullable=True),
        sa.Column('balance', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['fee_plan_id'], ['fee_plans.id'], ),
        sa.ForeignKeyConstraint(['student_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # 15. Payments
    op.create_table(
        'payments',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('student_id', sa.String(), nullable=True),
        sa.Column('amount', sa.Integer(), nullable=True),
        sa.Column('method', sa.String(), nullable=True),
        sa.Column('reference', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(['student_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # 16. Notifications
    notification_status_enum = sa.Enum('UNREAD', 'READ', name='notificationstatus')
    notification_type_enum = sa.Enum('GENERAL', 'TEST', 'FEES', 'ATTENDANCE', 'CERTIFICATE', name='notificationtype')
    op.create_table(
        'notifications',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=True),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('status', notification_status_enum, nullable=True),
        sa.Column('notification_type', notification_type_enum, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # 17. Approval Requests
    approval_request_type_enum = sa.Enum('DELETE_STUDENT', 'DELETE_EDUCATOR', 'DELETE_WORKSHOP', name='approvalrequesttype')
    approval_request_status_enum = sa.Enum('PENDING', 'APPROVED', 'REJECTED', name='approvalrequeststatus')
    op.create_table(
        'approval_requests',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('request_type', approval_request_type_enum, nullable=False),
        sa.Column('status', approval_request_status_enum, nullable=True),
        sa.Column('payload', sa.JSON(), nullable=True),
        sa.Column('requested_by', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['requested_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # 18. Salary Payments
    salary_payment_status_enum = sa.Enum('PAID', 'UNPAID', name='salarypaymentstatus')
    op.create_table(
        'salary_payments',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('educator_id', sa.String(), nullable=False),
        sa.Column('month', sa.String(), nullable=False),
        sa.Column('amount', sa.Integer(), nullable=True),
        sa.Column('status', salary_payment_status_enum, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(['educator_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('salary_payments')
    op.drop_table('approval_requests')
    op.drop_table('notifications')
    op.drop_table('payments')
    op.drop_table('student_fees')
    op.drop_table('fee_plans')
    op.drop_table('certificates')
    op.drop_table('submissions')
    op.drop_table('questions')
    op.drop_table('assessments')
    op.drop_table('attendance')
    op.drop_table('sessions')
    op.drop_table('enrollments')
    op.drop_table('modules')
    op.drop_table('workshops')
    with op.batch_alter_table('users') as batch_op:
        batch_op.drop_constraint('fk_users_institution_id', type_='foreignkey')
    op.drop_table('institutions')
    op.drop_table('users')

    # Drop Enums
    sa.Enum(name='salarypaymentstatus').drop(op.get_bind())
    sa.Enum(name='approvalrequeststatus').drop(op.get_bind())
    sa.Enum(name='approvalrequesttype').drop(op.get_bind())
    sa.Enum(name='notificationtype').drop(op.get_bind())
    sa.Enum(name='notificationstatus').drop(op.get_bind())
    sa.Enum(name='questiontype').drop(op.get_bind())
    sa.Enum(name='enrollmentstatus').drop(op.get_bind())
    sa.Enum(name='userrole').drop(op.get_bind())