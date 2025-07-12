from flask import Blueprint,jsonify,request

from backend.schemas import PlanificationSchema
from models import TypeChaine, CodeModeles,Planification
from schemas import ChaineSchema, ModelesSchema
from flask_jwt_extended import jwt_required, get_jwt, current_user

manage_chaine_roles_bp=Blueprint('manage_roles_chaine', __name__)


@manage_chaine_roles_bp.post("/addchaineOrRole")
@jwt_required()
def addChaineOrRole():
    if current_user.role == "userManager":
        data=request.get_json()
        role=TypeChaine.get_type_chaine_byID(id=data.get("id"))
        if role is not None:
            return jsonify({"error": "role already exists"},409)
        else:

            new_role=TypeChaine(
                id=data.get("id"),
              )

            new_role.save_chaine()
            return jsonify({"message": "chaine or role  added successfully"},200)
    return jsonify({"message": "Vous n'etes pas autorisé pour cette focntion"},401)

@manage_chaine_roles_bp.get("/getAllRoles")
@jwt_required()
def getAllRoles():
    if current_user.role in ["userManager","production"]:
       roles=TypeChaine.get_all_chaines()
       roles_result = ChaineSchema().dump(roles, many=True)
       return jsonify({
            "roles":roles_result,
            },200)
    return jsonify({
       "message":"unauthorized"
    },401),


@manage_chaine_roles_bp.get("/getChaineOrRoleByID")
@jwt_required()
def getRoleById():
    if current_user.role == "userManager":
        data = request.get_json()
        id = data.get("id")
        role = TypeChaine.get_type_chaine_byID(id=id)
        if role is not None:
            return jsonify({
                "user": ChaineSchema.dump(role),
            }, 200)
        return jsonify({
            "message": "user n'existe pas dans la base"
        },404)


@manage_chaine_roles_bp.delete("/deletechaine")
@jwt_required()
def deleteChaine():
    if current_user.role == "userManager":
        data = request.get_json()
        id = data.get("id")
        role = TypeChaine.get_type_chaine_byID(id=id)
        if role is not None:
            role.delete_chaine()
            return jsonify({
                "message": "role deleted successfully",
            }, 200)
        return jsonify({
            "message": "role n'existe pas dans la base"
        },404)

@manage_chaine_roles_bp.get("/get_all_models")
@jwt_required()
def get_all_models():
    if current_user.role == "userManager":
        modeles=CodeModeles.get_all_codemodeles()
        modelesSchema=ModelesSchema().dump(modeles,many=True)
        print(modelesSchema)
        return jsonify({
            "modeles":modelesSchema
        },200)

@manage_chaine_roles_bp.post("/addOrUpdatePlanification")
@jwt_required()
def addORUpdatePlanification():
    if current_user.role == "userManager":
        data=request.get_json()
        modele=data.get("modele")
        chaine=data.get("chaine")
        listeRegimeHoraire=data.get("listeRegimeHoraire")
        for regimeHoraire in listeRegimeHoraire:
            regime=regimeHoraire.get("regime")
            joursSemaine=regimeHoraire.get("joursSemaine")
            plan=Planification(
                modele=modele,
                chaine = chaine,
                regimeHoraire =regime,
                horaireLundi = joursSemaine.get("horaireLundi"),
                nbPaireLundi = joursSemaine.get("nbPaireLundi"),
                horaireMardi = joursSemaine.get("horaireMardi"),
                nbPaireMardi = joursSemaine.get("nbPaireMardi"),
                horaireMercredi = joursSemaine.get("horaireMercredi"),
                nbPaireMercredi = joursSemaine.get("nbPaireMercredi"),
                horaireJeudi = joursSemaine.get("horaireJeudi"),
                nbPaireJeudi = joursSemaine.get("nbPaireJeudi"),
                horaireVendredi = joursSemaine.get("horaireVendredi"),
                nbPaireVendredi = joursSemaine.get("nbPaireVendredi"),
                horaireSamedi = joursSemaine.get("horaireSamedi"),
                nbPaireSamedi = joursSemaine.get("nbPaireSamedi"),
            )
            planexiste = Planification.get_planification_by_modele_regimeHor_chaine(chaine,modele,regime)
            print("plan existe",planexiste)
            if planexiste is not None:
                print("notttttttttttt none")
                planexiste.update_planification(plan)

            else:
                plan.save_planification()
        return jsonify({"message": "planification updated successfully"}, 201)
    return jsonify({
        "message":"vous n'etes pas autoris<UNK> pour cette focntion"
    })
@manage_chaine_roles_bp.get("/getPlanBymodelChaineAndRegime")
@jwt_required()
def getPlanBymodelChaineAndRegime():
    if current_user.role == "userManager":
        data = request.get_json()
        modele = data.get("modele")
        chaine = data.get("chaine")
        regime = data.get("regime")
        plan = Planification.get_planification_by_modele_regimeHor_chaine(chaine=chaine,modele=modele,regimeHoraire=regime)
        planSchema=PlanificationSchema().dump(plan)
        if plan is not None:
            return jsonify({
                "plan": planSchema,
            }, 200)
        return jsonify({
            "message": "user n'existe pas dans la base"
        },404)
@manage_chaine_roles_bp.get("/getPlanBymodelChaine")
@jwt_required()
def getPlanBymodelChaine():
    if current_user.role == "userManager":
        data = request.get_json()
        modele = data.get("modele")
        chaine = data.get("chaine")
        plan = Planification.get_planification_by_modele_chaine(chaine=chaine,modele=modele)
        planSchema=PlanificationSchema().dump(plan,many=True)
        if plan is not None:
            return jsonify({
                "plan": planSchema,
            }, 200)
        return jsonify({
            "message": "user n'existe pas dans la base"
        },404)