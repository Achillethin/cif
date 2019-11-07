import warnings
import copy


def get_config(dataset, model, use_baseline):
    return {
        "dataset": dataset,
        "model": model,
        **get_config_base(dataset, model, use_baseline)
    }


def get_config_base(dataset, model, use_baseline):
    if dataset in ["2uniforms", "8gaussians", "checkerboard", "2spirals", "rings"]:
        return get_2d_config(dataset, model, use_baseline)

    elif dataset in ["power", "gas", "hepmass", "miniboone"]:
        return get_uci_config(dataset, model, use_baseline)

    elif dataset in ["mnist", "fashion-mnist", "cifar10", "svhn"]:
        return get_images_config(dataset, model, use_baseline)

    else:
        assert False, f"Invalid dataset {dataset}"


def get_2d_config(dataset, model, use_baseline):
    assert model in ["flat-realnvp", "maf", "sos", "nsf"], f"Invalid model {model} for dataset {dataset}"

    if dataset == "2uniforms":
        if use_baseline:
            config = {
                "num_density_layers": 10,
                "g_hidden_channels": [50] * 4,
                "num_u_channels": 0
            }

        else:
            config = {
                "num_density_layers": 5,
                "g_hidden_channels": [10] * 2,
                "num_u_channels": 1,
                "st_nets": [10] * 2,
                "p_nets": [50] * 4,
                "q_nets": [50] * 4
            }

        config = {
            **config,
            "max_bad_valid_epochs": 300,
            "max_epochs": 300,
        }

    else:
        if use_baseline:
            config = {
                "num_density_layers": 20,
                "g_hidden_channels": [50] * 4,
                "num_u_channels": 0
            }

        else:
            config = {
                "num_density_layers": 5,
                "g_hidden_channels": [50] * 4,
                "num_u_channels": 1,
                "st_nets": [10] * 2,
                "p_nets": [50] * 4,
                "q_nets": [50] * 4,
            }

        config = {
            **config,
            "max_bad_valid_epochs": 500,
            "max_epochs": 500
        }

    config = {
        **config,

        "dequantize": False,

        "batch_norm": True,
        "batch_norm_apply_affine": True,
        "batch_norm_use_running_averages": False,
        "batch_norm_momentum": 0.1,

        "early_stopping": True,
        "train_batch_size": 1000,
        "valid_batch_size": 1000,
        "test_batch_size": 10000,

        "opt": "adam",
        "lr": 1e-3,
        "weight_decay": 0.,
        "epochs_per_test": 5,

        "num_train_elbo_samples": 10 if not use_baseline else 1,
        "num_valid_elbo_samples": 10 if not use_baseline else 1,
        "num_test_elbo_samples": 100 if not use_baseline else 1
    }

    if model == "sos":
        warnings.warn("Overriding `num_density_layers`")
        config["num_density_layers"] = 3 if use_baseline else 2
        config["num_polynomials_per_layer"] = 2
        config["polynomial_degree"] = 4

        config["st_nets"] = [40] * 2
        config["p_nets"] = [40] * 4
        config["q_nets"] =  [40] * 4

    elif model == "nsf":
        warnings.warn("Overriding `num_density_layers`")
        config["num_density_layers"] = 2
        config["num_bins"] = 64 if use_baseline else 24 
        config["resnet_hidden_channels"] = 32
        config["num_resnet_blocks"] = 2
        config["use_batchnorm_in_resnet"] = True
        config["apply_unconditional_transform"] = False
        config["tail_bound"] = 5
        config["use_autoregressive"] = False
        config["dropout_probability"] = 0.0
        config["use_invconv"] = False
        config["add_invconv_to_end"] = False

        config["st_nets"] = [24] * 2
        config["p_nets"] = [24] * 3
        config["q_nets"] =  [24] * 3

    return config


def get_uci_config(dataset, model, use_baseline):
    assert model in ["flat-realnvp", "maf", "sos", "nsf"], f"Invalid model {model} for dataset {dataset}"

    if dataset in ["gas", "power"]:
        if use_baseline:
            config = {
                "num_density_layers": 10,
                "g_hidden_channels": [200] * 2,
                "num_u_channels": 0
            }

        else:
            config = {
                "num_density_layers": 10,
                "g_hidden_channels": [100] * 2,
                "num_u_channels": 2,
                "st_nets": [100] * 2,
                "p_nets": [200] * 2,
                "q_nets": [200] * 2,
            }

    elif dataset in ["hepmass", "miniboone"]:
        if use_baseline:
            config = {
                "num_density_layers": 10,
                "g_hidden_channels": [512] * 2,
                "num_u_channels": 0
            }

        else:
            config = {
                "num_density_layers": 10,
                "g_hidden_channels": [128] * 2,
                "num_u_channels": 5 if dataset == "hepmass" else 10,
                "st_nets": [128] * 2,
                "p_nets": [512] * 2,
                "q_nets": [512] * 2
            }

    config = {
        **config,

        "dequantize": False,

        "batch_norm": True,
        "batch_norm_apply_affine": True,
        "batch_norm_use_running_averages": False,

        "early_stopping": True,
        "train_batch_size": 1000,
        "valid_batch_size": 5000,
        "test_batch_size": 5000,

        "opt": "adam",
        "lr": 1e-3,
        "weight_decay": 0.,
        "max_bad_valid_epochs": 5000,
        "max_epochs": 5000,
        "epochs_per_test": 5,

        "num_train_elbo_samples": 1 if not use_baseline else 1,
        "num_valid_elbo_samples": 5 if not use_baseline else 1,
        "num_test_elbo_samples": 10 if not use_baseline else 1
    }

    if model == "sos":
        assert use_baseline
        config = {
            **config,
            "num_density_layers": 8,
            "num_polynomials_per_layer": 5,
            "polynomial_degree": 4,
            "lr": 1e-3,
            "opt": "sgd"
        }

    elif model == "nsf":
        warnings.warn("Overriding `num_density_layers`")

        config["use_batchnorm_in_resnet"] = False
        config["apply_unconditional_transform"] = True
        config["tail_bound"] = 3
        config["use_autoregressive"] = False
        config["use_invconv"] = True
        config["add_invconv_to_end"] = True

        if not config["use_autoregressive"]:

            if dataset == "power":
                config["num_density_layers"] = 10
                config["num_resnet_blocks"] = 2
                config["resnet_hidden_channels"] = 256
                config["num_bins"] = 8 
                config["dropout_probability"] = 0.0

            if dataset == "gas":
                config["num_density_layers"] = 10
                config["num_resnet_blocks"] = 2
                config["resnet_hidden_channels"] = 256
                config["num_bins"] = 8 
                config["dropout_probability"] = 0.1
                
            if dataset == "hepmass":
                config["num_density_layers"] = 20
                config["num_resnet_blocks"] = 1
                config["resnet_hidden_channels"] = 128
                config["num_bins"] = 8 
                config["dropout_probability"] = 0.2
                
            if dataset == "miniboone":
                config["num_density_layers"] = 10
                config["num_resnet_blocks"] = 1
                config["resnet_hidden_channels"] = 32
                config["num_bins"] = 4 
                config["dropout_probability"] = 0.2

        else:
            raise NotImplementedError            

    return config


def get_images_config(dataset, model, use_baseline):
    if model == "multiscale-realnvp":
        if use_baseline:
            config = {
                "g_hidden_channels": [64] * 8,
                "num_u_channels": 0
            }

        else:
            config = {
                "g_hidden_channels": [64] * 4,
                "num_u_channels": 1,
                "st_nets": [8] * 2,
                "p_nets": [64] * 2,
                "q_nets": [64] * 2
            }

        config["early_stopping"] = True
        config["train_batch_size"] = 100
        config["valid_batch_size"] = 500
        config["test_batch_size"] = 500
        config["opt"] = "adam"
        config["lr"] = 1e-4
        config["weight_decay"] = 0.

        if dataset in ["cifar10", "svhn"]:
            config["logit_tf_lambda"] = 0.05
            config["logit_tf_scale"] = 256

        elif dataset in ["mnist", "fashion-mnist"]:
            config["logit_tf_lambda"] = 1e-6
            config["logit_tf_scale"] = 256

    elif model == "glow":
        if use_baseline:
            config = {
                "num_scales": 3,
                "num_steps_per_scale": 32,
                "g_num_hidden_channels": 512,
                "num_u_channels": 0,
                "valid_batch_size": 500,
                "test_batch_size": 500
            }

        else:
            config = {
                "num_scales": 2,
                "num_steps_per_scale": 32,
                "g_num_hidden_channels": 256,
                "num_u_channels": 1,
                "st_nets": 64,
                "p_nets": 128,
                "q_nets": 128,
                "valid_batch_size": 100,
                "test_batch_size": 100
            }

        config["early_stopping"] = False
        config["train_batch_size"] = 64
        config["opt"] = "adamax"
        config["lr"] = 5e-4

        if dataset in ["cifar10"]:
            config["weight_decay"] = 0.1
        else:
            config["weight_decay"] = 0.

        config["centering_tf_scale"] = 256

    else:
        assert False, f"Invalid model {model} for dataset {dataset}"

    config = {
        **config,

        "dequantize": True,

        "batch_norm": True,
        "batch_norm_apply_affine": True,
        "batch_norm_use_running_averages": True,
        "batch_norm_momentum": 0.1,

        "max_bad_valid_epochs": 50,
        "max_epochs": 1000,
        "epochs_per_test": 1,

        "num_train_elbo_samples": 1 if not use_baseline else 1,
        "num_valid_elbo_samples": 5 if not use_baseline else 1,
        "num_test_elbo_samples": 10 if not use_baseline else 1
    }

    return config
