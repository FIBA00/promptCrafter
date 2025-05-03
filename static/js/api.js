/**
 * PromptCrafter API Client
 * A JavaScript client for interacting with the PromptCrafter API
 */

class PromptCrafterAPI {
  constructor(baseURL = '') {
    this.baseURL = baseURL;
    this.headers = {
      'Content-Type': 'application/json',
    };
  }

  /**
   * Generate a prompt using the API
   * @param {Object} data - The prompt data
   * @param {string} data.role - The role or context
   * @param {string} data.task - The task or objective
   * @param {string} data.constraints - The constraints or tools
   * @param {string} data.output - The output format
   * @param {string} data.personality - The personality or tone
   * @returns {Promise<Object>} - The generated prompts
   */
  async generatePrompt(data) {
    try {
      const response = await fetch(`${this.baseURL}/api/generate`, {
        method: 'POST',
        headers: this.headers,
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to generate prompt');
      }

      return await response.json();
    } catch (error) {
      console.error('API Error:', error);
      throw error;
    }
  }

  /**
   * Save a prompt to the user's collection
   * @param {Object} data - The prompt data
   * @returns {Promise<Object>} - The saved prompt information
   */
  async savePrompt(data) {
    try {
      const formData = new FormData();
      Object.keys(data).forEach(key => {
        formData.append(key, data[key]);
      });

      const response = await fetch(`${this.baseURL}/save_prompt`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to save prompt');
      }

      return await response.json();
    } catch (error) {
      console.error('API Error:', error);
      throw error;
    }
  }

  /**
   * Toggle the public/private status of a prompt
   * @param {number} promptId - The ID of the prompt
   * @param {boolean} isPublic - Whether the prompt should be public
   * @returns {Promise<Object>} - The result of the operation
   */
  async togglePublicStatus(promptId, isPublic) {
    try {
      const response = await fetch(`${this.baseURL}/toggle_public/${promptId}`, {
        method: 'POST',
        headers: this.headers,
        body: JSON.stringify({ is_public: isPublic }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to update prompt visibility');
      }

      return await response.json();
    } catch (error) {
      console.error('API Error:', error);
      throw error;
    }
  }

  /**
   * Delete a prompt from the user's collection
   * @param {number} promptId - The ID of the prompt
   * @returns {Promise<void>}
   */
  async deletePrompt(promptId) {
    try {
      // Note: This is a redirect-based deletion, not a JSON API
      window.location.href = `${this.baseURL}/delete_prompt/${promptId}`;
    } catch (error) {
      console.error('Navigation Error:', error);
      throw error;
    }
  }
}

// Create a global instance for use throughout the application
window.promptCrafterAPI = new PromptCrafterAPI(); 