DATASETS = {

    # -----------------------------------
    # FORECAST
    # -----------------------------------

    "baseline_forecast": {

        "path": "Data/baseline_forecast.csv",

        "required_columns": [

            "date",
            "queue",
            "demand"
        ]
    },

    "demand_drivers": {

        "path": "Data/demand_drivers.csv",

        "description": "Structural demand growth drivers"
    },

    # -----------------------------------
    # WORKFORCE
    # -----------------------------------

    "workforce_supply": {

        "path": "Data/workforce_supply.csv",

        "required_columns": [

            "date",
            "queue",
            "attrition",
            "new_hires"
        ]
    },

    "budget_changes": {

        "path": "Data/budget_changes.csv",

        "required_columns": [

            "date",
            "queue",
            "budget_fte"
        ]
    },
    
    "workforce_scenarios": {

        "path": "Data/workforce_scenarios.csv",

        "required_columns": [

            "sequence",
            "scenario_name",
            "impact_area",
            "impact_type",
            "impact_value",
            "start_date",
            "end_date"
        ]
    },

    # -----------------------------------
    # HOSTORIC DATA
    # -----------------------------------
    
    "historical_operational_data": {

        "path":
            "Data/historical_operational_data.csv",

        "required_columns": [

            "date",
            "queue",
            "historical_demand",
            "historical_aht",
            "historical_sla"
        ]
    },

    "historical_actuals_staging": {

        "path":
            "Data/historical_actuals_staging.csv",

        "required_columns": [

            "date",
            "queue",
            "historical_demand",
            "historical_aht",
            "historical_sla"
        ]
    },

    "historical_adjustments": {

        "path": "Data/historical_adjustments.csv",

        "required_columns": [

            "start_date",
            "end_date",
            "queue",
            "metric",
            "adjustment_action",
            "adjustment_value",
            "reason",
            "enabled"
        ]
    },

    "historical_upload_audit": {
        "path": "Data/historical_upload_audit.csv",
        "category": "governance"
    },

    # -----------------------------------
    # QUEUE MASTER
    # -----------------------------------

    "queue_master": {

        "path": "Data/queue_master.csv",

        "required_columns": [

            "queue",
            "is_active",
            "channel",
            "default_aht",
            "default_shrinkage",
            "default_occupancy",
            "default_attrition"
        ]
    },

    # -----------------------------------
    # QUEUE CONFIG
    # -----------------------------------

    "queue_config": {

        "path": "Data/queue_config.csv",

        "required_columns": [

            "queue",
            "opening_fte"
        ]
    },

    # -----------------------------------
    # BUDGET
    # -----------------------------------

    "budget": {

        "path": "Data/budget_forecast.csv",

        "required_columns": [

            "date",
            "queue",
            "budgeted_fte"
        ]
    },

    # -----------------------------------
    # RAMP PROFILES
    # -----------------------------------

    "ramp_profiles": {

        "path": "Data/ramp_profiles.csv",

        "required_columns": [

            "queue",
            "ramp_percentage"
        ]
    },

    # -----------------------------------
    # PROGRAMME PORTFOLIO
    # -----------------------------------

    "programme_portfolio": {

        "path": "Data/programme_portfolio.csv",

        "required_columns": [

            "programme",
            "queue",
            "start_date",
            "end_date",
            "ai_deflection",
            "demand_change",
            "aht_change",
            "productivity_gain",
            "occupancy_change",
            "shrinkage_change",
            "delay_weeks",
            "dependency"
        ]
    },

    # -----------------------------------
    # CAPABILITY
    # -----------------------------------

    "workforce_capabilities": {

        "path": "Data/workforce_capabilities.csv",

        "required_columns": [

            "skill_group",
            "seniority",
            "available_fte"
        ]
    },
    
    "executive_risk": {

    "path": "Output/executive_risk.csv",

    "required_columns": [

        "overall_risk",
        "service_delivery_risk",
        "budget_risk"
    ]
    },
    
    "layer_impacts": {

    "path": "Output/layer_impacts.csv",

    "required_columns": [

        "layer",
        "driver",
        "impact"
    ]
    },
    
    "weekly_impacts": {

    "path": "Output/weekly_impact_log.csv",

    "required_columns": [

        "date",
        "queue",
        "impact_type",
        "driver",
        "effect"
    ]
    },
    
    "resolved_forecast": {

    "path": "Output/resolved_forecast.csv",

    "required_columns": [

        "date",
        "queue",
        "resolved_forecast",
        "gross_requirement",
        "available_supply",
        "fte_gap"
    ]
    },

"active_plan": {

    "path": "Data/active_plan.csv",

    "required_columns": [

        "date",
        "queue",
        "resolved_forecast",
        "gross_requirement",
        "available_supply",
        "fte_gap"
    ]
},

    "forecast_intelligence": {

        "path":
            "Output/forecast_intelligence.csv",

        "required_columns": [

            "queue",
            "headline",
            "severity"
        ]
    },

    "scenario_layers": {

        "path": "Data/scenario_layers.csv",

        "required_columns": [

            "queue",
            "start_date",
            "end_date",
            "impact_pct"
        ]
    },
    
    
    "capability_requirements": {

    "path": "Data/capability_requirements.csv",

    "required_columns": [

        "skill_group",
        "seniority",
        "required_fte"
    ]
    },
    
    "financial_assumptions": {

    "path": "Data/financial_assumptions.csv",

    "required_columns": [

        "cost_type",
        "value"
    ]
    },
    
    "workforce_config": {

    "path": "Data/workforce_config.csv",

    "required_columns": [

        "queue",
        "opening_fte",
        "shrinkage",
        "occupancy",
        "aht"
    ]
    },
    
    "demand_overlays": {

    "path": "Data/demand_overlays.csv",

    "required_columns": [

        "queue",
        "start_date",
        "end_date",
        "overlay_type",
        "adjustment_value",
        "reason"
    ]
    },
    
    "forecast_layers": {

    "path": "Data/forecast_layers.csv",

    "description": "Forecast layer orchestration"
    },

    "transformation_benefits": {

    "path": "Data/transformation_benefits.csv",

    "required_columns": [

        "queue",
        "start_date",
        "end_date",
        "impact_pct"
    ]
    },

    "imported_forecast": {
        "path": "Data/imported_forecast.csv"
    },

    "forecast_configuration": {
        "path": "Data/forecast_configuration.csv"
    },

    "forecast_queue_config": {

        "path":
            "Data/forecast_queue_config.csv",

        "required_columns": [

            "queue",
            "forecast_source"
        ]
    },

}

