import streamlit as st
import pandas as pd
import plotly.graph_objects as go

ERROR_TYPES = [
    "Non-respect des consignes",
    "Négligence",
    "Communication insuffisante",
    "Précipitation",
    "Manque d'équipement"
]

PHASE_1_SITUATIONS = [
    {
        "text": "1. Tu vois un collègue sans casque, que fais-tu ?",
        "choices": [
            ("Lui rappeler immédiatement de le mettre", None),
            ("Ne rien dire", "Non-respect des consignes"),
            ("En parler après la pause", "Communication insuffisante")
        ]
    },
    {
        "text": "2. Tu dois soulever une charge lourde seul, que fais-tu ?",
        "choices": [
            ("Demander de l’aide pour soulever", None),
            ("Faire vite tout seul", "Précipitation"),
            ("Ignorer le risque", "Négligence")
        ]
    },
    {
        "text": "3. Une zone dangereuse a des panneaux masqués, que fais-tu ?",
        "choices": [
            ("Signaler immédiatement au chef de chantier", None),
            ("Continuer en faisant attention", "Manque d'équipement"),
            ("Ignorer", "Négligence")
        ]
    }
]

PHASE_2_SETS = {
    "Précipitation": [
        {
            "text": "Tu dois monter un échafaudage avec un délai serré, que fais-tu ?",
            "choices": [
                ("Je prends le temps de vérifier chaque élément", None),
                ("Je monte rapidement sans tout revérifier", "Précipitation"),
                ("Je délègue sans contrôler", "Négligence")
            ]
        },
        {
            "text": "Un nouveau plan de sécurité vient d'être distribué :",
            "choices": [
                ("Je le lis attentivement", None),
                ("Je le feuillette rapidement", "Précipitation"),
                ("Je le pose de côté pour plus tard", "Négligence")
            ]
        },
        {
            "text": "Un engin fait un bruit étrange :",
            "choices": [
                ("Je le signale et arrête de l'utiliser", None),
                ("Je continue pour finir la tâche", "Précipitation"),
                ("Je ne fais rien", "Négligence")
            ]
        }
    ],
    "Communication insuffisante": [
        {
            "text": "Tu remarques une erreur sur le plan d’intervention :",
            "choices": [
                ("Je préviens mon responsable", None),
                ("Je n'en parle qu'à un collègue", "Communication insuffisante"),
                ("Je fais avec sans signaler", "Négligence")
            ]
        },
        {
            "text": "Un conflit entre collègues perturbe le chantier :",
            "choices": [
                ("Je fais remonter l’information", None),
                ("Je laisse chacun gérer", "Communication insuffisante"),
                ("J'ignore la situation", "Négligence")
            ]
        },
        {
            "text": "Un nouvel arrivant ne comprend pas les consignes :",
            "choices": [
                ("Je prends le temps de lui expliquer", None),
                ("Je dis juste de suivre les autres", "Communication insuffisante"),
                ("Je l’ignore", "Négligence")
            ]
        }
    ],
    "Autres": [
        {
            "text": "Une alarme incendie retentit :",
            "choices": [
                ("Je suis les procédures à la lettre", None),
                ("Je continue mon travail pensant à une fausse alerte", "Négligence"),
                ("Je demande aux autres quoi faire", "Communication insuffisante")
            ]
        },
        {
            "text": "Un outil présenté comme dangereux est mal rangé :",
            "choices": [
                ("Je le range et informe l'équipe", None),
                ("Je le laisse en pensant qu'un autre le fera", "Négligence"),
                ("Je le cache sans rien dire", "Communication insuffisante")
            ]
        },
        {
            "text": "La météo se dégrade rapidement :",
            "choices": [
                ("Je suspend les activités risquées", None),
                ("Je poursuis pour respecter le planning", "Précipitation"),
                ("Je laisse les autres décider", "Non-respect des consignes")
            ]
        }
    ]
}

def init_profiles(nb):
    if "profiles" not in st.session_state:
        st.session_state.profiles = {}
    for i in range(1, nb + 1):
        pid = f"Employé {i}"
        if pid not in st.session_state.profiles:
            st.session_state.profiles[pid] = {
                "phase": "phase_1",
                "situation_index": 0,
                "error_counts_phase_1": {et: 0 for et in ERROR_TYPES},
                "error_counts_phase_2": {et: 0 for et in ERROR_TYPES},
                "history_phase_1": [],
                "history_phase_2": [],
                "phase_2_set": None,
            }

def choose_dominant_error(errors):
    if sum(errors.values()) == 0:
        return "Autres"
    dominant = max(errors, key=errors.get)
    return dominant if dominant in PHASE_2_SETS else "Autres"

def show_progress(current, total):
    st.write(f"Situation {current} / {total}")
    st.progress(current / total)

def radar_chart(errors_dict, title):
    categories = list(errors_dict.keys())
    values = list(errors_dict.values())
    # Ajouter le premier point à la fin pour fermer le cercle
    values += values[:1]
    categories += categories[:1]
    max_val = max(values) if max(values) > 0 else 1
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name=title
    ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, max_val + 1]
            )),
        showlegend=False,
        title=title
    )
    st.plotly_chart(fig, use_container_width=True)

def show_situation(profile):
    phase = profile["phase"]
    idx = profile["situation_index"]

    if phase == "phase_1":
        situations = PHASE_1_SITUATIONS
        history = profile["history_phase_1"]
        errors = profile["error_counts_phase_1"]
    else:
        if not profile["phase_2_set"]:
            profile["phase_2_set"] = choose_dominant_error(profile["error_counts_phase_1"])
        situations = PHASE_2_SETS[profile["phase_2_set"]]
        history = profile["history_phase_2"]
        errors = profile["error_counts_phase_2"]

    current = situations[idx]
    show_progress(idx + 1, len(situations))
    st.write(f"### {current['text']}")

    choices_text = [c[0] for c in current["choices"]]
    selected_choice = st.radio("Choisissez une option", choices_text, key=f"radio_{phase}_{idx}")

    if st.button("Valider ma réponse"):
        err = None
        for ctext, cerr in current["choices"]:
            if ctext == selected_choice:
                err = cerr
                break
        history.append({"situation_number": idx + 1, "choice": selected_choice, "error": err})
        if err:
            errors[err] += 1

        if idx + 1 < len(situations):
            profile["situation_index"] += 1
        else:
            profile["situation_index"] = 0
            profile["phase"] = "debrief_1" if phase == "phase_1" else "debrief_final"
        st.session_state.refresh_flag = not st.session_state.get("refresh_flag", False)

def show_debrief_1(profile):
    st.title("📋 Débriefing Round 1")
    radar_chart(profile["error_counts_phase_1"], "Erreurs Round 1")
    dominant = choose_dominant_error(profile["error_counts_phase_1"])
    st.markdown(f"**Erreur dominante : {dominant}**")

    if st.button("Passer à la suite du scénario"):
        profile["phase"] = "phase_2"
        profile["phase_2_set"] = dominant
        st.session_state.refresh_flag = not st.session_state.get("refresh_flag", False)

def show_debrief_final(profile):
    st.title("✅ Fin du scénario")
    total_errors = {et: profile["error_counts_phase_1"][et] + profile["error_counts_phase_2"][et] for et in ERROR_TYPES}
    radar_chart(total_errors, "Erreurs cumulées Round 1 & 2")
    dominant = choose_dominant_error(total_errors)
    st.markdown(f"**Erreur dominante globale : {dominant}**")

    st.subheader("Historique complet")
    st.write("Round 1")
    st.write(pd.DataFrame(profile["history_phase_1"]))
    st.write("Round 2")
    st.write(pd.DataFrame(profile["history_phase_2"]))

def main():
    st.title("Simulateur de prévention chantier - Multi-profils")
    nb_profs = st.sidebar.number_input("Nombre de profils", 3, 10, value=3)
    init_profiles(nb_profs)

    onglets = st.tabs(["Simulation", "Analyse"])

    with onglets[0]:
        st.subheader("Choix du profil")
        noms = list(st.session_state.profiles.keys())[:nb_profs]
        profil_nom = st.selectbox("Profil à simuler", noms)
        profil = st.session_state.profiles[profil_nom]

        if profil["phase"] in ["phase_1", "phase_2"]:
            show_situation(profil)
        elif profil["phase"] == "debrief_1":
            show_debrief_1(profil)
        elif profil["phase"] == "debrief_final":
            show_debrief_final(profil)

    with onglets[1]:
        st.subheader("Synthèse collective")

        noms = list(st.session_state.profiles.keys())[:nb_profs]

        errors_per_profile = {}
        for p_name in noms:
            p = st.session_state.profiles[p_name]
            total_errors = {et: p["error_counts_phase_1"][et] + p["error_counts_phase_2"][et] for et in ERROR_TYPES}
            errors_per_profile[p_name] = total_errors

        df_errors = pd.DataFrame(errors_per_profile)
        df_errors['Moyenne équipe'] = df_errors.mean(axis=1)

        # Radar chart Moyenne équipe
        categories = list(df_errors.index)
        values = df_errors['Moyenne équipe'].values
        # fermer la toile
        values = list(values) + [values[0]]
        categories = categories + [categories[0]]
        max_val = max(values) if max(values) > 0 else 1
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            name='Moyenne équipe'
        ))
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, max_val + 1]
                )),
            showlegend=False,
            title="Profil d'erreurs moyen de l'équipe"
        )
        st.plotly_chart(fig, use_container_width=True)

        st.write("Détail des erreurs par profil :")
        st.dataframe(df_errors)

        st.subheader("Analyse individuelle")
        indiv = st.selectbox("Voir un profil", noms, key="analyse_indiv")
        p = st.session_state.profiles[indiv]
        perr = {et: p["error_counts_phase_1"][et] + p["error_counts_phase_2"][et] for et in ERROR_TYPES}

        radar_chart(perr, f"Profil d'erreurs de {indiv}")

        st.write("Round 1")
        st.write(pd.DataFrame(p["history_phase_1"]))
        st.write("Round 2")
        st.write(pd.DataFrame(p["history_phase_2"]))

if __name__ == "__main__":
    main()
