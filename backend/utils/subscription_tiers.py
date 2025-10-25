"""
RaptorFlow Subscription Tier Configuration
===========================================

CANONICAL SOURCE: /TIER_DEFINITIONS.md

This file enforces the tier specs in the backend.
DO NOT modify tier specs here without updating TIER_DEFINITIONS.md first.

Tier Structure:
- Breeze (₹1,499/mo): Entry-level, solo founder
- Glide (₹2,499/mo): Team collaboration, agencies
- Soar (₹4,999/mo): Enterprise operations

All tiers get the core strategy brain. Differences are in:
- Scale (quotas, projects, personas)
- Collaboration (editor slots, team size)
- Depth (analysis, automation, tracking)
- Channels (dispatch destinations)
"""

SUBSCRIPTION_TIERS = {
    'breeze': {
        'name': 'Breeze',
        'price_inr': 1499,
        'currency': 'INR',
        'tagline': 'Give me clarity, fast.',
        'target': 'Solo founder, very lean team, single brand',

        # Capacity
        'capacity': {
            'projects': 5,
            'research_runs_per_month': 30,
            'assets_per_month': 40,
            'asset_split_light_percent': 70,  # default: 70% light, 30% pro
            'personas_active': 3,
            'evidence_chunks': 10000,
        },

        # Strategy Features (all tiers get base)
        'strategy_features': {
            'icp_persona_studio': True,
            'positioning_pov': True,
            'offer_pricing_builder': True,
            'pmf_pulse_cadence': True,
            'category_mapper': True,
            'anti_persona_guard': True,
            'wedge_finder': True,
            'objection_map': True,
        },

        # Creation Features
        'creation': {
            'message_matrix': True,
            'copy_studio': True,
            'creative_briefs': True,
            'landing_page_sections': True,
            'canva_fill': True,
        },

        # Dispatch
        'dispatch': {
            'channels': 1,
            'channel_options': ['email', 'linkedin', 'twitter', 'slack', 'zapier'],
            'utm_builder': True,
        },

        # Measurement
        'measurement': {
            'lift_lite': True,
            'creative_leaderboard': False,
            'kill_scale_recommendations': False,
        },

        # Governance
        'governance': {
            'tone_claim_guard': True,
            'plagiarism_scan': True,
            'brand_guard': False,
            'approval_history_export': False,
        },

        # Collaboration
        'collaboration': {
            'named_seats': 1,
            'guest_approvers': 2,
            'active_editor_slots': 1,  # solo, no concurrency limit
            'unlimited_invites': False,
        },

        # Features
        'features': {
            'strategy_workspace': True,
            'evidence_locker': True,
            'message_matrix': True,
            'copy_studio': True,
            'dispatch': True,
            'lift_measurement': True,
            'qr_generation': False,
            'batch_recipes': False,
            'rotators': False,
            'competitor_watch': False,
            'market_pulse': False,
            'offer_ladder_simulator': False,
            'priority_support': False,
        },
    },

    'glide': {
        'name': 'Glide',
        'price_inr': 2499,
        'currency': 'INR',
        'tagline': 'My team is in this with me now.',
        'target': 'Small teams, boutique agencies, growing brands',

        # Capacity
        'capacity': {
            'projects': float('inf'),  # Unlimited
            'research_runs_per_month': 120,
            'assets_per_month': 120,
            'asset_split_light_percent': None,  # Fully adjustable
            'personas_active': 3,
            'evidence_chunks': 50000,
        },

        # Strategy Features (all tiers get base + upgrades)
        'strategy_features': {
            'icp_persona_studio': True,
            'positioning_pov': True,
            'offer_pricing_builder': True,
            'pmf_pulse_cadence': True,
            'category_mapper': True,
            'anti_persona_guard': True,
            'wedge_finder': True,
            'objection_map': True,
            'adjacency_mapping_pro': True,  # Glide upgrade
            'offer_stress_test': True,  # Glide upgrade
            'pov_heatmap': True,  # Glide upgrade
        },

        # Creation Features
        'creation': {
            'message_matrix': True,
            'copy_studio': True,
            'creative_briefs': True,
            'landing_page_sections': True,
            'canva_fill': True,
            'advanced_message_matrix': True,
            'long_form_drafts': True,
            'multi_page_creative_briefs': True,
        },

        # Dispatch
        'dispatch': {
            'channels': 2,
            'channel_options': ['email', 'linkedin', 'twitter', 'slack', 'zapier'],
            'utm_builder': True,
            'qr_batch_generation': True,
        },

        # Measurement
        'measurement': {
            'lift_lite': True,
            'creative_leaderboard': True,
            'kill_scale_recommendations': True,
            'experiment_snapshots': False,
        },

        # Governance
        'governance': {
            'tone_claim_guard': True,
            'plagiarism_scan': True,
            'brand_guard': True,
            'approval_history_export': False,
            'restricted_terms_enforcement': True,
        },

        # Collaboration (Glide Differentiation)
        'collaboration': {
            'named_seats': None,  # Unlimited invites
            'unlimited_invites': True,
            'active_editor_slots': 3,  # Pooled concurrency
            'guest_approvers': 2,
            'shared_quota': True,
        },

        # Features
        'features': {
            'strategy_workspace': True,
            'evidence_locker': True,
            'message_matrix': True,
            'copy_studio': True,
            'dispatch': True,
            'lift_measurement': True,
            'qr_generation': True,
            'batch_recipes': False,
            'rotators': False,
            'competitor_watch': False,
            'market_pulse': False,
            'offer_ladder_simulator': False,
            'priority_support': False,
        },
    },

    'soar': {
        'name': 'Soar',
        'price_inr': 4999,
        'currency': 'INR',
        'tagline': 'I am running this like an operation.',
        'target': 'Agencies with multiple clients, performance teams',

        # Capacity
        'capacity': {
            'projects': float('inf'),  # Unlimited
            'research_runs_per_month': 180,
            'assets_per_month': 200,
            'asset_split_light_percent': None,  # Fully adjustable
            'personas_active': 5,
            'evidence_chunks': 100000,
        },

        # Strategy Features (all tiers get base + all upgrades)
        'strategy_features': {
            'icp_persona_studio': True,
            'positioning_pov': True,
            'offer_pricing_builder': True,
            'pmf_pulse_cadence': True,
            'category_mapper': True,
            'anti_persona_guard': True,
            'wedge_finder': True,
            'objection_map': True,
            'adjacency_mapping_pro': True,
            'offer_stress_test': True,
            'pov_heatmap': True,
            'competitor_watch': True,  # Soar upgrade
            'market_pulse': True,  # Soar upgrade
            'offer_ladder_simulator': True,  # Soar upgrade
        },

        # Creation Features
        'creation': {
            'message_matrix': True,
            'copy_studio': True,
            'creative_briefs': True,
            'landing_page_sections': True,
            'canva_fill': True,
            'advanced_message_matrix': True,
            'long_form_drafts': True,
            'multi_page_creative_briefs': True,
            'batch_recipes': True,  # Soar exclusive
        },

        # Dispatch
        'dispatch': {
            'channels': 3,
            'channel_options': ['email', 'linkedin', 'twitter', 'slack', 'zapier'],
            'utm_builder': True,
            'qr_batch_generation': True,
            'rotators': True,  # Soar exclusive
        },

        # Measurement
        'measurement': {
            'lift_lite': True,
            'creative_leaderboard': True,
            'kill_scale_recommendations': True,
            'experiment_snapshots': True,  # Soar exclusive
            'exportable_snapshots': True,
        },

        # Governance & Compliance
        'governance': {
            'tone_claim_guard': True,
            'plagiarism_scan': True,
            'brand_guard': True,
            'approval_history_export': True,  # Soar exclusive
            'restricted_terms_enforcement': True,
            'role_based_permissions': True,  # Owner, Editor, Approver, Viewer
        },

        # Collaboration
        'collaboration': {
            'named_seats': 5,  # Locked roles
            'active_editor_slots': 5,  # Pooled concurrency
            'guest_approvers': None,  # Uses role-based instead
            'priority_support': True,
            'escalation': True,
        },

        # Features
        'features': {
            'strategy_workspace': True,
            'evidence_locker': True,
            'message_matrix': True,
            'copy_studio': True,
            'dispatch': True,
            'lift_measurement': True,
            'qr_generation': True,
            'batch_recipes': True,
            'rotators': True,
            'competitor_watch': True,
            'market_pulse': True,
            'offer_ladder_simulator': True,
            'priority_support': True,
            'approval_audit_trail': True,
        },
    },
}

# Lookup helpers
TIER_NAMES = {v['name']: k for k, v in SUBSCRIPTION_TIERS.items()}
TIER_PRICES = {k: v['price_inr'] for k, v in SUBSCRIPTION_TIERS.items()}


def get_tier_config(tier_key: str) -> dict:
    """Get full tier configuration by key (breeze, glide, soar)"""
    tier_key = tier_key.lower()
    if tier_key not in SUBSCRIPTION_TIERS:
        raise ValueError(f"Invalid tier: {tier_key}. Must be one of: {list(SUBSCRIPTION_TIERS.keys())}")
    return SUBSCRIPTION_TIERS[tier_key]


def validate_tier_access(tier_key: str, feature: str) -> bool:
    """Check if tier has access to a feature"""
    config = get_tier_config(tier_key)
    return config.get('features', {}).get(feature, False)


def get_capacity_limit(tier_key: str, capacity_type: str) -> int | float:
    """Get capacity limit for a tier (projects, assets, etc.)"""
    config = get_tier_config(tier_key)
    return config.get('capacity', {}).get(capacity_type, 0)
