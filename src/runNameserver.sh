#!/bin/sh
export PYRO_SERIALIZERS_ACCEPTED=pickle
python -m Pyro4.naming -n 0.0.0.0
