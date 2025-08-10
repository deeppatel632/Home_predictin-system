from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import pickle
from pathlib import Path
import numpy as np

BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR.parent
ARTIFACT_DIR = PROJECT_DIR / 'artifacts'
MODEL_PATH = ARTIFACT_DIR / 'bangalore_home_prices_model.pkl'
COLUMNS_JSON = ARTIFACT_DIR / 'columns.json'

_model = None
_data_columns_raw = None
_data_columns_lower = None
_locations_raw = []
_locations_lower = []


def load_artifacts():
    global _model, _data_columns_raw, _data_columns_lower, _locations_raw, _locations_lower
    if _model is None:
        try:
            with open(MODEL_PATH, 'rb') as f:
                _model = pickle.load(f)
            print('model loaded', type(_model))
        except FileNotFoundError:
            print('MODEL_PATH_MISSING', MODEL_PATH)
        except Exception as exc:
            print('MODEL_LOAD_ERROR', exc)
    if _data_columns_raw is None or not _locations_raw:
        try:
            with open(COLUMNS_JSON, 'r') as f:
                payload = json.load(f)
            _data_columns_raw = payload.get('data_columns', [])
            _data_columns_lower = [c.lower() for c in _data_columns_raw]
            numeric = {'total_sqft', 'bath', 'bhk'}
            _locations_raw = [c for c in _data_columns_raw if c.lower() not in numeric]
            _locations_lower = [c.lower() for c in _locations_raw]
            print('columns loaded', len(_data_columns_raw), 'locations', len(_locations_raw))
        except FileNotFoundError:
            print('COLUMNS_JSON_MISSING', COLUMNS_JSON)
        except Exception as exc:
            print('COLUMNS_LOAD_ERROR', exc)


def index(request):
    load_artifacts()
    ctx = {
        'locations': sorted(_locations_raw),
        'predicted_price': None,
        'no_locations': not bool(_locations_raw),
    }
    return render(request, 'predictor/index.html', ctx)


def get_estimated_price(location: str, sqft: float, bath: int, bhk: int):
    load_artifacts()
    if _data_columns_lower is None or _model is None:
        return None
    try:
        sqft_idx = _data_columns_lower.index('total_sqft')
        bath_idx = _data_columns_lower.index('bath')
        bhk_idx = _data_columns_lower.index('bhk')
    except ValueError:
        return None
    try:
        loc_index = _data_columns_lower.index(location.lower())
    except ValueError:
        loc_index = -1
    fv = np.zeros(len(_data_columns_lower))
    fv[sqft_idx] = sqft
    fv[bath_idx] = bath
    fv[bhk_idx] = bhk
    if loc_index >= 0:
        fv[loc_index] = 1
    try:
        return round(float(_model.predict([fv])[0]), 2)
    except Exception as exc:
        print('PREDICT_ERROR', exc)
        return None


@csrf_exempt
def predict_price(request):
    if request.method == 'POST':
        if request.headers.get('Content-Type') == 'application/json':
            data = json.loads(request.body)
        else:
            data = request.POST
        location = data.get('location') or ''
        sqft = float(data.get('sqft'))
        bhk = int(data.get('bhk'))
        bath = int(data.get('bath'))
        price = get_estimated_price(location, sqft, bath, bhk)
        if request.headers.get('Accept') == 'application/json':
            if price is None:
                return JsonResponse({'error': 'Prediction unavailable (model or columns missing).'}, status=500)
            return JsonResponse({'estimated_price_lakh': price})
        return render(
            request,
            'predictor/index.html',
            {
                'locations': sorted(_locations_raw),
                'predicted_price': price if price is not None else None,
                'no_locations': not bool(_locations_raw),
            },
        )
    return JsonResponse({'error': 'POST required'}, status=405)
