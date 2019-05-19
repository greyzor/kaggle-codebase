"""
"""
import lightgbm as lgb

def lgb_train_cv(params, df_train, df_val, predictors, target='target',
	objective='binary', metrics='auc', feval=None, early_stopping_rounds=20,
	num_boost_round=3000, verbose_eval=10, categorical_features=None
):
    lgb_params = {
        'boosting_type': 'gbdt', 'objective': objective, 'metric':metrics,
        'learning_rate': 0.2,
        #'is_unbalance': 'true',  #because training data is unbalance (replaced with scale_pos_weight)
        'num_leaves': 31,  # we should let it be smaller than 2^(max_depth)
        'max_depth': -1,  # -1 means no limit
        'min_child_samples': 20,  # Minimum number of data need in a child(min_data_in_leaf)
        'max_bin': 255,  # Number of bucketed bin for feature values
        'subsample': 0.6,  # Subsample ratio of the training instance.
        'subsample_freq': 0,  # frequence of subsample, <=0 means no enable
        'colsample_bytree': 0.3,  # Subsample ratio of columns when constructing each tree.
        'min_child_weight': 5,  # Minimum sum of instance weight(hessian) needed in a child(leaf)
        'subsample_for_bin': 200000,  # Number of samples for constructing bin
        'min_split_gain': 0,  # lambda_l1, lambda_l2 and min_gain_to_split to regularization
        'reg_alpha': 0,  # L1 regularization term on weights
        'reg_lambda': 0,  # L2 regularization term on weights
        'nthread': 7, # 4
        'verbose': 0,
        'metric':metrics
    }
    lgb_params.update(params) # Overriding default params

    print("Preparing validation datasets")
    xgtrain = lgb.Dataset(
        df_train[predictors].values, label=df_train[target].values,
        feature_name=predictors, categorical_feature=categorical_features
    )
    xgvalid = lgb.Dataset(
        df_val[predictors].values, label=df_val[target].values,
        feature_name=predictors, categorical_feature=categorical_features
    )

    evals_results = {}
    bst1 = lgb.train(
        lgb_params, xgtrain,  valid_sets=[xgtrain, xgvalid], 
        valid_names=['train','valid'], 
        evals_result=evals_results, 
        num_boost_round=num_boost_round,
        early_stopping_rounds=early_stopping_rounds,
        verbose_eval=10, feval=feval
    )
    print("\nModel Report")
    print("bst1.best_iteration: ", bst1.best_iteration)
    eval_score = evals_results['valid'][metrics][bst1.best_iteration-1]
    print(metrics+":", eval_score)

    return (bst1, bst1.best_iteration, eval_score)