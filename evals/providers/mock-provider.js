module.exports = class SpecForgeMockProvider {
  constructor(options = {}) {
    this.providerId = options.id || 'specforge-mock-provider';
    this.config = options.config || {};
  }

  id() {
    return this.providerId;
  }

  async callApi(prompt, context) {
    const vars = (context && context.vars) || {};
    const input = JSON.stringify(vars);
    return {
      output: `Mock eval output for ${prompt}\n${input}`,
      metadata: {
        provider: this.providerId,
        config: this.config,
      },
    };
  }
};