import { useReducer, useEffect, useCallback } from 'react';
import { initialState, dataReducer } from '../reducers/dataReducer';

export function useDataObserver(initialData = null) {
  const [state, dispatch] = useReducer(dataReducer, {
    ...initialState,
    data: initialData
  });

  const startLoading = useCallback(() => {
    dispatch({ type: 'FETCH_START' });
  }, []);

  const handleSuccess = useCallback((payload) => {
    dispatch({ type: 'FETCH_SUCCESS', payload });
  }, []);

  const handleError = useCallback((error) => {
    dispatch({ type: 'FETCH_ERROR', payload: error.message });
  }, []);

  const updateData = useCallback((partialData) => {
    dispatch({ type: 'UPDATE_DATA', payload: partialData });
  }, []);

  const resetData = useCallback(() => {
    dispatch({ type: 'RESET_DATA' });
  }, []);

  return {
    state,
    actions: {
      startLoading,
      handleSuccess,
      handleError,
      updateData,
      resetData
    }
  };
}