# JTBD Transcription Technique - Baskerly

**Version**: 1.2.2
**Created**: 2026-01-01 17:30:00
**Last Updated**: 2026-01-01 20:15:00
**Status**: ✅ VALIDATED (2026-01-03 15:56)
**Supersedes**: transcription-technical-jtbd-v1.2.0.md, transcription-technical-jtbd-v1.0.0.md
**Related Docs**:
  - `jtbd-v0.md` (JTBD general journaliste)
  - `transcription-v0.md` (specs fonctionnelles)
  - `/.architecture/specifications/transcription-stack-analysis-v1.2.0.md`
**Agent**: product-manager

---

## Executive Summary

Ce document definit les Jobs-To-Be-Done techniques specifiques a la fonctionnalite de transcription de Baskerly. Il complete le JTBD metier general en detaillant les contraintes techniques et les criteres d'acceptation pour chaque job.

**Cible utilisateur** : Journalistes tous domaines (investigation, beaute, people, sports, etc.)

**Note v1.2.0** : Scores ODI revises pour refleter la realite du marche. Les outils actuels (Otter, Trint, Descript, Rev, Happy Scribe) sont globalement performants. Les vraies opportunites sont dans les niches mal servies : souverainete donnees, francais/accents regionaux, longs formats, integration workflow journalistique.

**Note v1.2.1** : Restructuration de la priorisation pour distinguer clairement Table Stakes (pre-requis marche) vs Differenciateurs (avantage concurrentiel). Le MVP doit inclure les deux.

**Note v1.2.2** : Promotion de J10 (Dictionnaire personnalise) en P0 Differenciateur. Les journalistes traitent des sujets specialises avec terminologie propre (noms propres, termes techniques juridiques/medicaux/politiques/sportifs). Les concurrents offrent des dictionnaires limites ou reserves aux tiers payants superieurs. Baskerly integre un dictionnaire riche des le MVP.

---

## Note Importante : ODI vs MVP

### Comprendre la difference

**Score ODI eleve ≠ MVP obligatoire**

Le score ODI (Opportunity Score) mesure l'**opportunite de differenciation** :
- ODI eleve = forte opportunite car insatisfaction actuelle elevee
- ODI faible = peu d'opportunite car le marche est deja bien servi

**Table Stakes = MVP obligatoire** (independamment de l'ODI)

Les Table Stakes sont les fonctionnalites que **tous les concurrents proposent**. Sans elles, les utilisateurs ne considerent meme pas l'outil. Leur ODI peut etre faible (car les concurrents les font bien), mais elles restent indispensables.

### Exemple concret

| Fonctionnalite | ODI | Table Stake? | MVP? | Explication |
|----------------|-----|--------------|------|-------------|
| SyncView (J1) | 10 | Oui | Oui | ODI faible car Otter/Trint le font bien, mais attendu par tous |
| Souverainete (J4) | 17 | Non | Oui | ODI eleve car aucun concurrent, differenciateur cle |
| Live (J9) | 7 | Non | Non | ODI faible et non attendu par tous les utilisateurs |

### Formule MVP

```
MVP = Table Stakes + Differenciateurs Cles
    = (Ce que tout le monde attend) + (Ce qui nous distingue)
```

---

## Jobs-To-Be-Done

### J1: Sync Audio/Mot (SyncView)

**Statement**: Quand je lis une transcription, je veux cliquer sur n'importe quel mot pour entendre l'audio correspondant, afin de verifier rapidement ce qui a ete dit sans chercher manuellement dans la timeline.

| Critere | Valeur | Delta v1.1 |
|---------|--------|------------|
| **Importance** | 8/10 | -2 |
| **Satisfaction actuelle** | 6/10 | +5 |
| **Opportunity Score** | **10** | -9 |
| **Priorite** | P0 (Table Stake) | - |

**Justification delta** : La plupart des outils (Otter, Descript, Trint) offrent deja le click-to-play. C'est une fonctionnalite attendue, pas differenciante. Satisfaction elevee car ca fonctionne bien dans les outils existants. Importance reduite car les journalistes s'en servent mais ce n'est pas leur preoccupation principale.

**Classification** : TABLE STAKE - Attendu par tous les utilisateurs, non negociable pour MVP.

**Contraintes**:
- Precision timestamp : ≤200ms (80% mots), ≤100ms (optimal)
- Latence click-to-play : <300ms total
- Fallback si precision insuffisante (navigation phrase)

**Acceptance Criteria**:
- [ ] Click sur mot → audio joue au bon timecode
- [ ] Indicateur visuel si timestamp incertain (confidence < 0.7)
- [ ] Mode fallback phrase si word-level indisponible
- [ ] Surlignage mot en cours de lecture

---

### J2: Precision Timecodes

**Statement**: Quand je genere des sous-titres ou un transcript, je veux des timecodes precis au niveau du mot, afin de creer des sous-titres professionnels et permettre le SyncView.

| Critere | Valeur | Delta v1.1 |
|---------|--------|------------|
| **Importance** | 7/10 | -2 |
| **Satisfaction actuelle** | 6/10 | +3 |
| **Opportunity Score** | **8** | -7 |
| **Priorite** | P0 (Table Stake) | - |

**Justification delta** : Les outils actuels fournissent des timecodes de qualite suffisante pour la plupart des usages. Les journalistes qui font du sous-titrage pro utilisent souvent des outils dedies. Ce n'est pas un point de friction majeur.

**Classification** : TABLE STAKE - Pre-requis technique pour SyncView et exports professionnels.

**Contraintes**:
- Word-level timestamps obligatoire (pas segment-level seul)
- Precision cible : 50-150ms median
- Distribution : 95% des mots ≤400ms d'erreur
- Formats export : SRT, VTT, JSON

**Acceptance Criteria**:
- [ ] Chaque mot a un timestamp start/end
- [ ] Score de confiance par mot disponible
- [ ] Export SRT/VTT avec timecodes word-level
- [ ] JSON avec structure `{ word, start, end, confidence }`

---

### J3: Diarization (Speaker ID)

**Statement**: Quand je transcris une interview multi-locuteurs, je veux identifier automatiquement qui parle, afin de distinguer les interventions sans ecouter l'integralite.

| Critere | Valeur | Delta v1.1 |
|---------|--------|------------|
| **Importance** | 8/10 | = |
| **Satisfaction actuelle** | 5/10 | +5 |
| **Opportunity Score** | **11** | -5 |
| **Priorite** | P0 (Table Stake) | - |

**Justification delta** : Otter, Descript et Trint offrent tous la diarization. Elle fonctionne correctement pour 2-3 speakers. La satisfaction n'est pas a 0 - les journalistes l'utilisent et ca marche "assez bien". Les limites apparaissent avec plus de speakers ou audio bruite.

**Classification** : TABLE STAKE - Attendu pour 2-3 speakers. Indispensable pour le use case interview.

**Contraintes**:
- Precision attribution speaker : >90%
- Nombre max speakers MVP : 5 (2-3 prioritaire)
- Detection automatique du nombre de speakers
- Possibilite de nommer les speakers manuellement

**Acceptance Criteria**:
- [ ] Chaque segment attribue a un speaker (SPEAKER_01, etc.)
- [ ] UI pour renommer speakers (ex: "Journaliste", "Invite")
- [ ] Couleur par speaker dans le transcript
- [ ] Export avec speaker labels

---

### J4: Souverainete Self-Hosted

**Statement**: Quand je transcris des contenus sensibles (enquetes, sources confidentielles), je veux que mes donnees restent sur mon infrastructure, afin de garantir la confidentialite et la conformite RGPD.

| Critere | Valeur | Delta v1.1 |
|---------|--------|------------|
| **Importance** | 9/10 | -1 |
| **Satisfaction actuelle** | 1/10 | = |
| **Opportunity Score** | **17** | -2 |
| **Priorite** | P0 (Differenciateur) | = |

**Justification delta** : C'est une vraie opportunite. Aucun outil grand public n'offre de solution self-hosted. Cependant, l'importance est legerement reduite car tous les journalistes n'ont pas de contenus sensibles - un chroniqueur beaute n'a pas les memes contraintes qu'un journaliste investigation. Reste P0 car c'est un differenciateur fort pour une niche strategique.

**Classification** : DIFFERENCIATEUR - Notre USP. Aucun concurrent ne le propose.

**Contraintes**:
- Option 100% self-hosted (pas de cloud obligatoire)
- Pas de transit donnees vers serveurs tiers
- Stockage local ou Supabase EU
- Licence compatible (MIT/Apache/BSD, pas AGPL sans isolation)

**Acceptance Criteria**:
- [ ] Mode offline fonctionnel
- [ ] Aucune donnee envoyee a des tiers sans consentement
- [ ] Option cloud EU (Supabase) pour sync multi-device
- [ ] Documentation RGPD disponible

---

### J5: Qualite Transcription

**Statement**: Quand je transcris un audio, je veux un texte precis avec peu d'erreurs, afin de minimiser le temps de relecture et correction.

| Critere | Valeur | Delta v1.1 |
|---------|--------|------------|
| **Importance** | 9/10 | = |
| **Satisfaction actuelle** | 7/10 | +5 |
| **Opportunity Score** | **11** | -5 |
| **Priorite** | P0 (Table Stake) | - |

**Justification delta** : Les outils actuels (surtout en anglais) ont une excellente qualite. Meme en francais, Otter et Trint donnent des resultats tres corrects sur audio propre. Les journalistes sont globalement satisfaits - ils savent que quelques corrections sont normales. La vraie frustration concerne les termes techniques et noms propres, mais ils considerent que c'est "normal".

**Classification** : TABLE STAKE - Le minimum syndical. Sans transcription de qualite, pas de produit.

**Contraintes**:
- WER audio propre FR : <3%
- WER audio bruite FR : <7%
- WER multi-locuteurs : <5%
- Support accents regionaux FR

**Acceptance Criteria**:
- [ ] Transcription lisible sans correction majeure (audio propre)
- [ ] Indicateur qualite audio avant transcription
- [ ] Suggestions correction post-traitement
- [ ] Metriques WER disponibles (optionnel)

---

### J6: Formats Audio Supportes

**Statement**: Quand j'importe un fichier audio/video, je veux que tous les formats courants soient acceptes, afin de ne pas perdre de temps en conversion.

| Critere | Valeur | Delta v1.1 |
|---------|--------|------------|
| **Importance** | 6/10 | -1 |
| **Satisfaction actuelle** | 8/10 | +3 |
| **Opportunity Score** | **4** | -5 |
| **Priorite** | P0 (Table Stake) | - |

**Justification delta** : Tous les outils supportent MP3, WAV, MP4. Ce n'est plus un probleme. Les journalistes ne pensent meme pas a ce sujet - ca "juste marche". Importance et opportunite tres faibles.

**Classification** : TABLE STAKE - Non negociable meme si ODI faible. L'absence serait eliminatoire.

**Contraintes**:
- Formats obligatoires : MP3, WAV, M4A, MP4, MOV
- Formats optionnels : OGG, FLAC, WEBM, MKV
- Taille max : 2GB
- Duree max : 4h
- Extraction audio automatique des videos

**Acceptance Criteria**:
- [ ] Import drag & drop tous formats courants
- [ ] Message erreur clair si format non supporte
- [ ] Progress bar pour gros fichiers
- [ ] Extraction audio video transparente

---

### J7: Export Standard

**Statement**: Quand ma transcription est terminee, je veux l'exporter dans des formats standard, afin de l'integrer dans mon workflow editorial.

| Critere | Valeur | Delta v1.1 |
|---------|--------|------------|
| **Importance** | 8/10 | N/A |
| **Satisfaction actuelle** | 7/10 | N/A |
| **Opportunity Score** | **9** | N/A |
| **Priorite** | P0 (Table Stake) | - |

**Classification** : TABLE STAKE - Export indispensable pour l'integration workflow.

**Contraintes**:
- Formats texte : TXT, DOCX, PDF
- Formats sous-titres : SRT, VTT
- Format structure : JSON
- Options : avec/sans timecodes, avec/sans speakers

**Acceptance Criteria**:
- [ ] Export TXT simple (texte brut)
- [ ] Export DOCX avec mise en forme speakers
- [ ] Export SRT/VTT pour sous-titrage
- [ ] Export JSON complet avec metadata
- [ ] Options de personnalisation export

---

### J8: Post-traitement

**Statement**: Quand la transcription brute est terminee, je veux des outils pour l'ameliorer automatiquement, afin de reduire le travail de relecture.

| Critere | Valeur | Delta v1.1 |
|---------|--------|------------|
| **Importance** | 6/10 | -1 |
| **Satisfaction actuelle** | 6/10 | +3 |
| **Opportunity Score** | **6** | -5 |
| **Priorite** | P2 | - |

**Justification delta** : La ponctuation automatique est standard maintenant. Descript et Otter le font bien. Les journalistes s'attendent a avoir une ponctuation correcte et l'obtiennent. Ce n'est plus un differenciateur.

**Contraintes**:
- Ponctuation automatique
- Capitalisation phrases
- Detection paragraphes
- Correction orthographique contextuelle

**Acceptance Criteria**:
- [ ] Ponctuation ajoutee automatiquement
- [ ] Paragraphes detectes (silences, changement sujet)
- [ ] Option correction orthographique
- [ ] Historique modifications (undo)

---

### J9: Transcription Live (Temps Reel)

**Statement**: Quand je suis en interview ou conference, je veux voir la transcription apparaitre en temps reel, afin de prendre des notes et verifier la capture sans attendre.

| Critere | Valeur | Delta v1.1 |
|---------|--------|------------|
| **Importance** | 6/10 | -1 |
| **Satisfaction actuelle** | 5/10 | +5 |
| **Opportunity Score** | **7** | -7 |
| **Priorite** | P2 | - |

**Justification delta** : Otter propose le live et ca fonctionne. Les journalistes qui en ont besoin l'utilisent deja. Ce n'est pas un besoin universel - beaucoup preferent enregistrer puis transcrire. Importance reduite car ce n'est pas le workflow principal de tous les journalistes.

**Contraintes**:
- Latence affichage : <2s apres parole
- Streaming audio continu (micro ou source externe)
- Mise a jour incrementale (pas de refresh complet)
- Mode "live notes" avec marqueurs temporels

**Acceptance Criteria**:
- [ ] Texte apparait <2s apres parole
- [ ] Indicateur "en cours d'ecoute"
- [ ] Possibilite de marquer des moments cles
- [ ] Sauvegarde continue (pas de perte si crash)
- [ ] Transition fluide vers mode edition post-live

---

### J10: Dictionnaire Personnalise

**Statement**: Quand je travaille sur un domaine specialise (juridique, medical, noms propres), je veux ajouter des termes a un dictionnaire, afin que la transcription reconnaisse correctement le vocabulaire specifique.

| Critere | Valeur | Delta v1.2.2 |
|---------|--------|--------------|
| **Importance** | 8/10 | +1 |
| **Satisfaction actuelle** | 4/10 | -2 |
| **Opportunity Score** | **12** | +4 |
| **Priorite** | P0 (Differenciateur) | Upgrade de P2 |

**Justification upgrade v1.2.2** : Reevaluation strategique. Les journalistes couvrent des sujets specialises avec terminologie propre : noms propres (personnes, lieux, organisations), termes techniques (juridique, medical, politique, sport, tech, etc.). Les concurrents proposent des dictionnaires limites (Otter : 100 termes max), reserves aux tiers payants superieurs (Trint Business, Rev Enterprise), ou mal integres au workflow. Baskerly se differencie en offrant un dictionnaire riche et accessible des le MVP.

**Classification** : DIFFERENCIATEUR - Concurrents sous-performants sur ce point. Opportunite de se demarquer.

**Analyse concurrentielle** :
| Concurrent | Dictionnaire | Limitation |
|------------|--------------|------------|
| Otter.ai | Oui | 100 termes max, Pro uniquement |
| Trint | Oui | Business tier uniquement |
| Descript | Non | Aucun support |
| Rev | Oui | Enterprise uniquement |
| Happy Scribe | Oui | 50 termes, plans superieurs |

**Avantage Baskerly** : Dictionnaire illimite, accessible des le plan de base, avec import/export et dictionnaires partageables entre projets.

**Contraintes**:
- Dictionnaire par projet ou global
- Import/export dictionnaire (CSV, JSON)
- Noms propres (personnes, lieux, organisations)
- Termes techniques metier
- Acronymes et abreviations
- Pas de limite de termes (ou limite elevee >1000)

**Acceptance Criteria**:
- [ ] UI pour ajouter/supprimer termes
- [ ] Dictionnaire applique avant transcription
- [ ] Suggestions basees sur dictionnaire pendant correction
- [ ] Import depuis fichier externe
- [ ] Dictionnaires partageables entre projets
- [ ] Pas de limite restrictive sur le nombre de termes

---

### J11: Precision et Confiance

**Statement**: Quand je lis une transcription, je veux savoir quels passages sont incertains, afin de concentrer ma relecture sur les zones problematiques.

| Critere | Valeur | Delta v1.1 |
|---------|--------|------------|
| **Importance** | 6/10 | -2 |
| **Satisfaction actuelle** | 4/10 | +3 |
| **Opportunity Score** | **8** | -7 |
| **Priorite** | P2 | - |

**Justification delta** : Peu d'outils affichent les scores de confiance explicitement, mais les transcriptions sont suffisamment bonnes pour que les journalistes n'en ressentent pas le besoin urgent. Ils relisent naturellement les passages qui "sonnent faux". C'est un nice-to-have, pas un must-have.

**Contraintes**:
- Score confiance par mot (0-1)
- Seuils visuels : high (>0.9), medium (0.7-0.9), low (<0.7)
- Indicateur global qualite transcription
- Filtrage mots incertains

**Acceptance Criteria**:
- [ ] Mots incertains visuellement distincts (couleur, style)
- [ ] Score confiance global affiche (ex: 94%)
- [ ] Navigation vers prochain mot incertain
- [ ] Option masquer/afficher indicateurs confiance

---

### J12: Support Audio/Video Longs

**Statement**: Quand je travaille sur des contenus de longue duree (conferences de presse, documentaires, auditions), je veux pouvoir les transcrire sans limitation arbitraire, afin de couvrir tous mes besoins professionnels sans decoupage manuel.

| Critere | Valeur | Delta v1.1 |
|---------|--------|------------|
| **Importance** | 8/10 | -1 |
| **Satisfaction actuelle** | 4/10 | +2 |
| **Opportunity Score** | **12** | -4 |
| **Priorite** | P1 | - |

**Justification delta** : Les limites existent (Otter 90min, Happy Scribe 5h) mais Rev et Trint gerent bien les longs formats. La satisfaction n'est pas a 2 - les journalistes qui travaillent sur des formats longs ont trouve des solutions (decoupage manuel ou outils adaptes). C'est une friction mais pas un blocage total.

**Benchmark Concurrence**:

| Outil | Limite Duree | Limite Taille |
|-------|--------------|---------------|
| Otter.ai | 90 min/fichier (pro) | 500MB |
| Descript | 4h | 2GB |
| Trint | Illimite (facture/min) | 5GB |
| Rev | Illimite | Illimite |
| Happy Scribe | 5h | 1GB |

**Definition "Long" pour Baskerly**:
- Standard : jusqu'a 4h (couvre 95% des use cases)
- Extended : jusqu'a 8h (conferences, auditions longues)
- Pro/Enterprise : jusqu'a 24h (documentaires, archives)

**Contraintes**:
- Duree minimale MVP : 4h sans degradation
- Duree cible : 8h avec chunking intelligent
- Taille fichier max : 4GB (MP4 1080p ~4h)
- Gestion memoire : streaming/chunking (pas de load complet en RAM)
- Reprise sur interruption (checkpoint toutes les 15min)

**Cas d'usage prioritaires**:
- Conferences de presse (2-3h)
- Interviews longues investigation (1-2h)
- Auditions/proces (3-6h)
- Documentaires archives (1-4h)
- Podcasts long format (2-3h)

**Acceptance Criteria**:
- [ ] Transcription fichier 4h sans erreur ni timeout
- [ ] Progression affichee pour fichiers >1h
- [ ] Chunks traites en parallele si possible (GPU)
- [ ] Resume possible apres interruption/crash
- [ ] Preview partiel disponible avant fin complete
- [ ] Export progressif (chapitres/segments disponibles avant fin)

---

### J13: Multi-langues Transcription

**Statement**: Quand j'interview des sources internationales ou travaille sur du contenu multilingue, je veux que la transcription detecte et traite correctement les differentes langues, afin d'obtenir un transcript precis sans pre-configuration manuelle.

| Critere | Valeur | Delta v1.1 |
|---------|--------|------------|
| **Importance** | 7/10 | -1 |
| **Satisfaction actuelle** | 5/10 | +4 |
| **Opportunity Score** | **9** | -6 |
| **Priorite** | P1 | - |

**Justification delta** : La detection de langue fonctionne bien dans les outils actuels. Le vrai probleme est le code-switching (melange FR/EN dans une meme phrase) qui reste difficile. Mais la plupart des journalistes travaillent dans une langue principale et sont satisfaits. Ce n'est pas une douleur majeure.

**Langues Prioritaires (Phase 1)**:

| Priorite | Langue | Code | Justification |
|----------|--------|------|---------------|
| P0 | Francais | fr | Marche principal |
| P0 | Anglais USA | en-US | Langue internationale |
| P0 | Anglais UK | en-GB | Sources britanniques |
| P1 | Espagnol | es | 3e langue mondiale |
| P1 | Allemand | de | Marche europeen |
| P1 | Italien | it | Marche europeen |
| P2 | Portugais | pt | Bresil, Portugal |
| P2 | Neerlandais | nl | Benelux |

**Contraintes**:
- Detection automatique de la langue (sans configuration prealable)
- Confiance detection : >95% sur segments >10s
- Switching en cours de transcription (code-switching FR/EN courant)
- WER cible par langue : comparable au francais (<5% audio propre)

**Modes de fonctionnement**:
1. **Auto-detect** : Detection langue dominante, appliquee a tout le fichier
2. **Multi-lingual** : Detection par segment, tags langue dans output
3. **Force** : Utilisateur specifie la langue (override detection)

**Acceptance Criteria**:
- [ ] Detection automatique langue avec >95% precision
- [ ] Indication langue detectee dans UI avant transcription
- [ ] Support code-switching (ex: interview FR avec citations EN)
- [ ] Export avec tags langue par segment (JSON, SRT)
- [ ] Option forcer langue si detection incorrecte
- [ ] Dictionnaire personnalise par langue

---

### J14: Gestion des Accents

**Statement**: Quand je transcris des locuteurs avec accents regionaux ou non-natifs, je veux une precision acceptable, afin de ne pas passer des heures a corriger des erreurs systematiques.

| Critere | Valeur | Delta v1.1 |
|---------|--------|------------|
| **Importance** | 8/10 | +1 |
| **Satisfaction actuelle** | 3/10 | +1 |
| **Opportunity Score** | **13** | +1 |
| **Priorite** | P0 (Differenciateur) | + |

**Justification delta** : C'est une vraie opportunite. Les accents quebecois, africains francophones et non-natifs sont mal geres par les outils actuels. Les journalistes francophones qui interviewent des sources variees rencontrent ce probleme frequemment. Importance augmentee car c'est un point de douleur reel pour le marche francophone.

**Classification** : DIFFERENCIATEUR - Niche francophone mal servie par les concurrents.

**Types d'accents a supporter**:

**Accents regionaux francophones**:
| Accent | Difficulte | Priorite |
|--------|------------|----------|
| Quebec | Elevee | P0 |
| Suisse | Moyenne | P1 |
| Belgique | Faible | P1 |
| Afrique (Senegal, Cote d'Ivoire) | Moyenne | P1 |
| Sud France (Marseille, Toulouse) | Faible | P2 |
| Nord France (Ch'ti) | Moyenne | P2 |

**Accents non-natifs (L2 speakers)**:
| Locuteur | Langue cible | Difficulte |
|----------|--------------|------------|
| Francophone → Anglais | EN | Moyenne |
| Anglophone → Francais | FR | Moyenne |
| Germanophone → Francais/Anglais | FR/EN | Elevee |
| Hispanophone → Francais | FR | Elevee |

**Contraintes**:
- WER accent leger (<5% degradation vs natif)
- WER accent fort (<15% degradation vs natif)
- Pas de degradation pour accents legers (standard)
- Indication confiance reduite si accent detecte

**Metriques de reference (WER)**:
| Type audio | Natif standard | Accent leger | Accent fort |
|------------|----------------|--------------|-------------|
| Audio propre | 3% | 5% | 10% |
| Audio bruite | 7% | 10% | 18% |

**Acceptance Criteria**:
- [ ] Transcription quebecois lisible sans correction majeure
- [ ] Indicateur si accent detecte (impact potentiel precision)
- [ ] Option "accent hint" pour pre-configurer (ex: "Quebec")
- [ ] Pas de blocage/refus sur accents forts
- [ ] Feedback loop : correction utilisateur ameliore futur (opt-in)

---

### J15: Chevauchement de Voix (Overlapping Speech)

**Statement**: Quand plusieurs personnes parlent en meme temps (interruptions, debats animes), je veux que le systeme capture au maximum ce qui est dit, afin de ne pas perdre d'informations cruciales.

| Critere | Valeur | Delta v1.1 |
|---------|--------|------------|
| **Importance** | 6/10 | -1 |
| **Satisfaction actuelle** | 3/10 | +3 |
| **Opportunity Score** | **9** | -5 |
| **Priorite** | P1 | - |

**Justification delta** : L'overlap reste un defi technique pour tous les outils. Mais les journalistes ont appris a vivre avec - ils savent que ces passages necessitent une re-ecoute manuelle. Ce n'est pas une frustration majeure car ils considerent que c'est "normal" que la machine echoue sur ces passages.

**Definition Overlapping**:
- Leger (<20% du segment) : 2 voix, une dominante
- Modere (20-50%) : 2 voix d'intensite similaire
- Severe (>50%) : 3+ voix ou brouhaha

**Contraintes**:
- Overlap leger : transcription voix dominante, marqueur overlap
- Overlap modere : tentative transcription des 2 voix, confiance reduite
- Overlap severe : segment marque "[inaudible - overlap]" + timestamp
- Impact diarization : attribution speaker degradee en overlap

**Seuils de tolerance**:
| Type overlap | Transcription attendue | Diarization |
|--------------|------------------------|-------------|
| Leger (<20%) | Voix dominante OK | Speaker correct |
| Modere (20-50%) | Partielle, confiance medium | Speaker incertain |
| Severe (>50%) | Non garantie | Speaker multiple/inconnu |

**Acceptance Criteria**:
- [ ] Marqueur visuel pour segments avec overlap detecte
- [ ] Transcription partielle plutot que silence/skip
- [ ] Indication [overlap] dans export avec timestamp
- [ ] Score confiance reduit automatiquement
- [ ] Lien audio direct pour verification manuelle
- [ ] Statistique globale : % audio avec overlap

---

### J16: Support Multi-locuteurs (>5 Speakers)

**Statement**: Quand je transcris des tables rondes, debats ou conferences avec nombreux intervenants, je veux que le systeme identifie et attribue correctement les interventions a chaque speaker, afin de produire un transcript exploitable sans re-ecoute complete.

| Critere | Valeur | Delta v1.1 |
|---------|--------|------------|
| **Importance** | 7/10 | -1 |
| **Satisfaction actuelle** | 4/10 | +4 |
| **Opportunity Score** | **10** | -6 |
| **Priorite** | P1 | - |

**Justification delta** : La diarization multi-speakers fonctionne "assez bien" pour 3-5 speakers dans les outils actuels. Les erreurs existent mais les journalistes les corrigent manuellement - c'est du travail supplementaire mais pas un blocage. La vraie douleur est au-dela de 6+ speakers, use case moins frequent.

**Benchmark Concurrence**:

| Outil | Speakers max | Precision declaree |
|-------|--------------|-------------------|
| Otter.ai | 10 | ~85% |
| Descript | Illimite (manuel) | N/A |
| Trint | 5 | ~80% |
| Rev (human) | Illimite | >99% |
| AWS Transcribe | 10 | ~90% |

**Definition Seuils Baskerly**:
- Standard : 2-5 speakers (interview, petit groupe) - couvert par J3
- Extended : 6-10 speakers (table ronde, reunion)
- Maximum : 15 speakers (conference, debat televise)

**Contraintes**:
- Precision diarization 6-10 speakers : >80%
- Precision diarization 11-15 speakers : >70% (best effort)
- Detection automatique nombre speakers (±1 erreur acceptable)
- Fusion/separation manuelle de speakers possible

**Cas d'usage par nombre de speakers**:
| Speakers | Cas typique | Priorite |
|----------|-------------|----------|
| 6-8 | Table ronde, reunion equipe | P1 |
| 9-10 | Debat televise, conference | P1 |
| 11-15 | Grande conference, audition | P2 |

**Acceptance Criteria**:
- [ ] Detection automatique nombre speakers (6-10)
- [ ] Attribution correcte >80% pour 6-10 speakers
- [ ] Attribution correcte >70% pour 11-15 speakers
- [ ] UI pour fusionner 2 speakers mal detectes
- [ ] UI pour splitter 1 speaker detecte comme 2 personnes
- [ ] Couleur unique par speaker (palette 15 couleurs)
- [ ] Nom editable par speaker avec propagation globale
- [ ] Export avec speaker labels (SPEAKER_01 ou nom custom)
- [ ] Indicateur confiance attribution par segment

---

## ODI Matrix (v1.2.2)

| Job | Description | I | S | ODI | Classification |
|-----|-------------|---|---|-----|----------------|
| J4 | Souverainete Self-Hosted | 9 | 1 | **17** | Differenciateur |
| J14 | Gestion des Accents | 8 | 3 | **13** | Differenciateur |
| J10 | Dictionnaire Personnalise | 8 | 4 | **12** | Differenciateur |
| J12 | Support Audio/Video Longs | 8 | 4 | **12** | Nice to have |
| J3 | Diarization (2-5 spk) | 8 | 5 | **11** | Table Stake |
| J5 | Qualite Transcription | 9 | 7 | **11** | Table Stake |
| J16 | Support Multi-locuteurs (>5) | 7 | 4 | **10** | Nice to have |
| J1 | Sync Audio/Mot (SyncView) | 8 | 6 | **10** | Table Stake |
| J7 | Export Standard | 8 | 7 | **9** | Table Stake |
| J13 | Multi-langues Transcription | 7 | 5 | **9** | Nice to have |
| J15 | Chevauchement de Voix | 6 | 3 | **9** | Nice to have |
| J2 | Precision Timecodes | 7 | 6 | **8** | Table Stake |
| J11 | Precision et Confiance | 6 | 4 | **8** | Future |
| J9 | Transcription Live | 6 | 5 | **7** | Future |
| J8 | Post-traitement | 6 | 6 | **6** | Future |
| J6 | Formats Supportes | 6 | 8 | **4** | Table Stake |

**Formule ODI** : O = I + max(I - S, 0)

**Note v1.2.2** : J10 reevalue (Importance 8, Satisfaction 4) pour refleter la frustration reelle des journalistes specialises face aux limites des dictionnaires concurrents.

---

## Priorisation (v1.2.2)

### P0 - MVP (Table Stakes + Differenciateurs Cles)

Le MVP doit inclure tout ce que les utilisateurs **attendent** (Table Stakes) plus ce qui nous **distingue** (Differenciateurs).

#### Table Stakes (Pre-requis marche - sans ca, pas de consideration)

| Job | ODI | Description | Justification |
|-----|-----|-------------|---------------|
| J5 | 11 | Qualite Transcription | Le minimum syndical. WER <5% FR audio propre. |
| J1 | 10 | SyncView (Click-to-play) | Attendu par tous. Otter/Trint le font. |
| J2 | 8 | Timecodes precis | Pre-requis technique pour SyncView et exports. |
| J3 | 11 | Diarization basique (2-5 spk) | Use case interview = coeur du produit. |
| J6 | 4 | Formats supportes (MP3, MP4, etc.) | Invisible mais eliminatoire si absent. |
| J7 | 9 | Export standard (TXT, SRT, DOCX) | Indispensable pour integration workflow. |

**Note** : Ces fonctionnalites ont parfois un ODI faible car les concurrents les font bien. Mais leur absence = elimination immediate par l'utilisateur.

#### Differenciateurs MVP (Ce qui nous distingue)

| Job | ODI | Description | Justification |
|-----|-----|-------------|---------------|
| J4 | 17 | Souverainete Self-Hosted | Notre USP. Aucun concurrent grand public. |
| J14 | 13 | Accents francophones | Niche mal servie (Quebec, Afrique). |
| J10 | 12 | Dictionnaire Personnalise | Concurrents limitent ou reservent aux plans chers. Baskerly offre un dictionnaire riche et illimite des le MVP. |

**Note** : Ces fonctionnalites ont un ODI eleve car les concurrents ne les adressent pas ou les font mal. C'est notre avantage competitif.

---

### P1 - Post-MVP (Nice to Have)

Extensions naturelles du MVP, a developper apres validation marche.

| Job | ODI | Description | Justification |
|-----|-----|-------------|---------------|
| J12 | 12 | Support audio longs (>4h) | Use case investigation. Limites concurrence. |
| J16 | 10 | Multi-speakers avance (>5) | Extension de J3, use cases specifiques. |
| J13 | 9 | Multi-langues avance | Code-switching = edge case. Detection basique suffit. |
| J15 | 9 | Chevauchement de voix | Probleme connu, utilisateurs tolerants. |

---

### P2 - Future (Low Priority)

Fonctionnalites a considerer selon feedback utilisateurs.

| Job | ODI | Description | Justification |
|-----|-----|-------------|---------------|
| J11 | 8 | Scores de confiance | Nice-to-have, pas de demande forte. |
| J9 | 7 | Transcription live | Niche. Otter le fait deja bien. |
| J8 | 6 | Post-traitement avance | Standard. Pas de differentiation. |

---

## Resume Visuel Priorisation

```
+-----------------------------------------------------------------------+
|                        P0 - MVP                                       |
+-----------------------------------------------------------------------+
|                                                                       |
|  TABLE STAKES (Pre-requis)          DIFFERENCIATEURS (USP)            |
|  +---------------------------+      +-----------------------------+   |
|  | J5: Qualite (WER <5%)     |      | J4: Souverainete (ODI 17)   |   |
|  | J1: SyncView              |      | J14: Accents FR (ODI 13)    |   |
|  | J2: Timecodes             |      | J10: Dictionnaire (ODI 12)  |   |
|  | J3: Diarization 2-5 spk   |      +-----------------------------+   |
|  | J6: Formats MP3/MP4       |                                        |
|  | J7: Exports TXT/SRT       |                                        |
|  +---------------------------+                                        |
|                                                                       |
+-----------------------------------------------------------------------+

+-----------------------------------------------------------------------+
|                    P1 - Post-MVP                                      |
+-----------------------------------------------------------------------+
|  J12: Longs formats (>4h)  |  J16: Multi-spk >5  |  J13: Multi-lang  |
|  J15: Overlap handling                                                |
+-----------------------------------------------------------------------+

+-----------------------------------------------------------------------+
|                    P2 - Future                                        |
+-----------------------------------------------------------------------+
|  J11: Confiance scores  |  J9: Live  |  J8: Post-traitement          |
+-----------------------------------------------------------------------+
```

---

## Recapitulatif MVP (v1.2.2)

### Jobs P0

| Categorie | Jobs | Total |
|-----------|------|-------|
| Table Stakes | J5, J1, J2, J3, J6, J7 | 6 |
| Differenciateurs | J4, J14, J10 | 3 |
| **Total P0** | | **9** |

### ODI Cumule

| Categorie | Jobs | ODI Total |
|-----------|------|-----------|
| Table Stakes | J5(11) + J1(10) + J2(8) + J3(11) + J6(4) + J7(9) | 53 |
| Differenciateurs | J4(17) + J14(13) + J10(12) | 42 |
| **Total P0** | | **95** |

### Risques si Absence

| Job | Risque si absent |
|-----|------------------|
| J5 | Produit inutilisable - qualite = fondation |
| J1 | Workflow casse - verification impossible |
| J2 | SyncView impossible, exports degrades |
| J3 | Interview = use case #1, sans diarization = pas de marche |
| J6 | Friction immediate, abandon au premier fichier |
| J7 | Pas d'integration workflow = pas d'adoption |
| J4 | Perte de l'USP principale - deviens un "Otter de plus" |
| J14 | Perte du marche francophone hors France metropolitaine |
| J10 | Journalistes specialises mal servis, frustration sur noms propres/termes techniques |

---

## Changelog

### v1.2.2 (2026-01-01)
- **J10 promu P0 Differenciateur** : Reevaluation strategique. Importance 7→8, Satisfaction 6→4, ODI 8→12.
- Ajout analyse concurrentielle detaillee sur les dictionnaires (limites Otter, Trint, Rev, Happy Scribe).
- Ajout justification : terminologie specialisee (juridique, medical, politique, sport) + noms propres = pain point reel.
- Mise a jour matrice ODI avec nouvelles valeurs J10.
- Mise a jour tableau recapitulatif P0 : 6 Table Stakes + 3 Differenciateurs = 9 jobs.
- Resume visuel mis a jour.

### v1.2.1 (2026-01-01)
- Restructuration pour distinguer Table Stakes vs Differenciateurs
- Clarification : ODI faible ≠ exclusion MVP
- Section "ODI vs MVP" ajoutee
- J7 (Export Standard) ajoute explicitement aux Table Stakes
- Resume visuel de la priorisation

### v1.2.0 (2026-01-01)
- Revision complete des scores ODI
- Baisse globale des opportunites (concurrents performants)
- J4 et J14 confirmes comme differenciateurs
- J12-J16 detailles avec contraintes specifiques

### v1.1.0 (Initial)
- Definition initiale des 16 jobs
- Scores ODI optimistes (avant analyse concurrentielle)
