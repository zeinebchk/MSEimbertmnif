"""add table planification_chaine_modele

Revision ID: 723058177c97
Revises: 63f12dc570e2
Create Date: 2025-07-12 13:00:48.559847

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '723058177c97'
down_revision = '63f12dc570e2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('planification_chaine_modeles',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('modele', sa.String(length=100), nullable=True),
    sa.Column('chaine', sa.String(length=20), nullable=False),
    sa.Column('regimeHoraire', sa.Integer(), nullable=True),
    sa.Column('dateCreation', sa.Date(), nullable=True),
    sa.Column('horaireLundi', sa.Float(), nullable=True),
    sa.Column('nbPaireLundi', sa.Integer(), nullable=True),
    sa.Column('horaireMardi', sa.Float(), nullable=True),
    sa.Column('nbPaireMardi', sa.Integer(), nullable=True),
    sa.Column('horaireMercredi', sa.Float(), nullable=True),
    sa.Column('nbPaireMercredi', sa.Integer(), nullable=True),
    sa.Column('horaireJeudi', sa.Float(), nullable=True),
    sa.Column('nbPaireJeudi', sa.Integer(), nullable=True),
    sa.Column('horaireVendredi', sa.Float(), nullable=True),
    sa.Column('nbPaireVendredi', sa.Integer(), nullable=True),
    sa.Column('horaireSamedi', sa.Float(), nullable=True),
    sa.Column('nbPaireSamedi', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['chaine'], ['type_chaine.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('ofs_chaine', schema=None) as batch_op:
        batch_op.create_foreign_key(None, 'ofs', ['numCommandeOF'], ['numOF'])
        batch_op.create_foreign_key(None, 'type_chaine', ['idChaine'], ['id'])
        batch_op.create_foreign_key(None, 'planification_chaine_modeles', ['idPlanification'], ['id'])

    with op.batch_alter_table('ouvrier_chaine_ofs', schema=None) as batch_op:
        batch_op.create_foreign_key(None, 'ouvriers', ['matOuvrier'], ['MATR'])
        batch_op.create_foreign_key(None, 'type_chaine', ['idChaine'], ['id'])
        batch_op.create_foreign_key(None, 'ofs', ['numCommandeOF'], ['numOF'])

    with op.batch_alter_table('planification', schema=None) as batch_op:
        batch_op.create_foreign_key(None, 'type_chaine', ['chaine'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('planification', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')

    with op.batch_alter_table('ouvrier_chaine_ofs', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_constraint(None, type_='foreignkey')

    with op.batch_alter_table('ofs_chaine', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_constraint(None, type_='foreignkey')

    op.drop_table('planification_chaine_modeles')
    # ### end Alembic commands ###
