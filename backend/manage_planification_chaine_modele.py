from datetime import datetime

from flask import Blueprint,jsonify,request

from models import Planification, PlanificationChaineModeles
from schemas import PlanificationSchema, PlanificationChaineModeleSchema
from flask_jwt_extended import jwt_required, get_jwt, current_user

manage_planification_modele_chaine_bp=Blueprint('manage_planification_chaine_modele', __name__)



@manage_planification_modele_chaine_bp.post("/addOrUpdatePlanification")
@jwt_required()
def addORUpdatePlanification():
    if current_user.role == "production":
        data=request.get_json()
        modele=data.get("modele")
        chaine=data.get("chaine")
        plan=PlanificationChaineModeles(
                modele=modele,
                chaine = chaine,
                regimeHoraire =data.get("regimeHoraire"),
                dateCreation=datetime.now().date(),
                horaireLundi = data.get("horaireLundi"),
                nbPaireLundi = data.get("nbPaireLundi"),
                horaireMardi = data.get("horaireMardi"),
                nbPaireMardi = data.get("nbPaireMardi"),
                horaireMercredi = data.get("horaireMercredi"),
                nbPaireMercredi = data.get("nbPaireMercredi"),
                horaireJeudi = data.get("horaireJeudi"),
                nbPaireJeudi = data.get("nbPaireJeudi"),
                horaireVendredi = data.get("horaireVendredi"),
                nbPaireVendredi = data.get("nbPaireVendredi"),
                horaireSamedi = data.get("horaireSamedi"),
                nbPaireSamedi = data.get("nbPaireSamedi"),
            )
        plan.save_planification()
        return jsonify({
            "message": "planification add successfully",
            "id": plan.id,
            "regimeHoraire":plan.regimeHoraire}
            ,201)
    return jsonify({
        "message":"vous n'etes pas autoris<UNK> pour cette focntion"
    })
@manage_planification_modele_chaine_bp.get("/getPlanBymodelChaineAndRegime")
@jwt_required()
def getPlanBymodelChaineAndRegime():
    if current_user.role == "userManager" or current_user.role == "production":
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
    return jsonify({
        "message": "unauthorized"
    }, 401)
@manage_planification_modele_chaine_bp.get("/getPlanBymodelChaine")
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
@manage_planification_modele_chaine_bp.get("/get_planifications_par_numcmd")
@jwt_required()
def get_planifications_par_numcmd():
    if current_user.role in ["userManager", "production"]:
        data = request.get_json()
        numcmd = data.get("numcmd")
        plan = PlanificationChaineModeles.get_planifications_par_numcmd(numcmd)
        planSchema=PlanificationChaineModeleSchema().dump(plan,many=True)
        if plan is not None:
            return jsonify({
                "plan": planSchema,
            }, 200)
        return jsonify({
            "message": "user n'existe pas dans la base"
        },404)