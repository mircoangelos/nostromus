export const initialState = {
    data: null,
    loading: false,
    error: null,
    lastUpdated: null
  };
  
  export function dataReducer(state, action) {
    switch (action.type) {
      case 'FETCH_START':
        return { 
          ...state, 
          loading: true, 
          error: null 
        };
        
      case 'FETCH_SUCCESS':
        return {
          ...state,
          loading: false,
          data: action.payload,
          lastUpdated: new Date().toISOString()
        };
        
      case 'FETCH_ERROR':
        return {
          ...state,
          loading: false,
          error: action.payload
        };
        
      case 'UPDATE_DATA':
        return {
          ...state,
          data: {
            ...state.data,
            ...action.payload
          },
          lastUpdated: new Date().toISOString()
        };
        
      case 'RESET_DATA':
        return initialState;
        
      default:
        throw new Error(`Unhandled action type: ${action.type}`);
    }
  }