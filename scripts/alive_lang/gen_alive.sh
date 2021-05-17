#!/bin/bash
set -e

seed=${1:-0}
vocab=""
train_file=""
dev_file=""
dropout=0.0
hidden_size=42
embed_size=42
action_embed_size=42
field_embed_size=42
type_embed_size=42
lr_decay=0.0
beam_size=1
lstm='lstm'
ls=0.1
model_name=model.atis.sup.${lstm}.hidden${hidden_size}.embed${embed_size}.action${action_embed_size}.field${field_embed_size}.type${type_embed_size}.dropout${dropout}.lr_decay${lr_decay}.beam${beam_size}.${vocab}.${train_file}.glorot.with_par_info.no_copy.ls${ls}.seed${seed}

echo "**** Writing results to logs/atis/${model_name}.log ****"
mkdir -p logs/atis
echo commit hash: `git rev-parse HEAD` > logs/atis/${model_name}.log

python -u gen_alive.py \
    --seed ${seed} \
    --mode train \
    --batch_size 10 \
    --asdl_file asdl/lang/alive_lang/alive_asdl.txt \
    --transition_system alive_lang \
    --train_file data/atis/${train_file} \
    --dev_file data/atis/${dev_file} \
    --vocab data/atis/${vocab} \
    --lstm ${lstm} \
    --primitive_token_label_smoothing ${ls} \
    --no_parent_field_type_embed \
    --no_parent_production_embed \
    --hidden_size ${hidden_size} \
    --att_vec_size ${hidden_size} \
    --embed_size ${embed_size} \
    --action_embed_size ${action_embed_size} \
    --field_embed_size ${field_embed_size} \
    --type_embed_size ${type_embed_size} \
    --dropout ${dropout} \
    --patience 5 \
    --max_num_trial 5 \
    --glorot_init \
    --no_copy \
    --lr_decay ${lr_decay} \
    --beam_size ${beam_size} \
    --decode_max_time_step 110 \
    --log_every 50 \
    --save_to saved_models/atis/${model_name} 2>&1 | tee -a logs/atis/${model_name}.log

#. scripts/atis/test.sh saved_models/atis/${model_name}.bin 2>&1 | tee -a logs/atis/${model_name}.log
