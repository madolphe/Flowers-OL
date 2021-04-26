class ParameterManager{
    constructor() {
      // Stimulus parameters
      this.repetition = 0;
      this.ind_stimcond = 0;
      this.flag_block = false;
      this.flag_load = false;
      this.count_color = -1;

      this.num_rep = num_rep_main;
      this.num_memory = num_memory_main;
  
      //save
      this.results_responses = [];
      this.results_rt = [];
      this.results_targetvalue_stim = [];
      this.results_num_stim = [];
      this.initialize();  
    }

      initialize(){
        this.num_memory = shuffle(this.num_memory);
        //ConditionManager
        let center_x = (Pos.center_x)-(size_target/2);
        let center_y =  (Pos.center_y)-(size_target/2);
        this.dict_pos = [
                          [center_x-1.5*shift_position,center_y-1.5*shift_position],
                          [center_x-0.5*shift_position,center_y-1.5*shift_position],
                          [center_x+0.5*shift_position,center_y-1.5*shift_position],
                          [center_x+1.5*shift_position,center_y-1.5*shift_position],
                          [center_x-1.5*shift_position,center_y-0.5*shift_position],
                          [center_x-0.5*shift_position,center_y-0.5*shift_position],
                          [center_x+0.5*shift_position,center_y-0.5*shift_position],
                          [center_x+1.5*shift_position,center_y-0.5*shift_position],
                          [center_x-1.5*shift_position,center_y+0.5*shift_position],
                          [center_x-0.5*shift_position,center_y+0.5*shift_position],
                          [center_x+0.5*shift_position,center_y+0.5*shift_position],
                          [center_x+1.5*shift_position,center_y+0.5*shift_position],
                          [center_x-1.5*shift_position,center_y+1.5*shift_position],
                          [center_x-0.5*shift_position,center_y+1.5*shift_position],
                          [center_x+0.5*shift_position,center_y+1.5*shift_position],
                          [center_x+1.5*shift_position,center_y+1.5*shift_position],
                        ];
    
        this.trial_stimcond = shuffle(array_stimcond); 
        this.tmp_res_ob = [];
        this.order = -1;  
      }

      next_trial(){
        this.save();
        //set the next trial parameters 
        this.ind_stimcond ++;
        this.flag_load = false;
        this.tmp_res_ob = [];
        this.count_color = -1;
        this.order = -1;
        this.trial_stimcond = shuffle(array_stimcond);
  
        if (this.ind_stimcond==this.num_memory.length-1){
          this.flag_block = true;
        }
      }
    
      next_block(){
        this.save();
        //set the next block parameters
        this.flag_load = false;
        this.tmp_res_ob = [];
        this.count_color = -1;
        this.order = -1;
  
  
        this.flag_block = false;
        this.repetition ++;
        this.trial_stimcond = shuffle(array_stimcond); 
        this.ind_stimcond = 0;
        this.num_memory = shuffle(this.num_memory);
      }
    
      save(){
        // save the current result.
        this.results_responses.push(this.tmp_res_ob);
        this.results_targetvalue_stim.push(this.trial_stimcond);
        this.results_num_stim.push(this.num_memory[this.ind_stimcond])
        //console.log('response is');
        //console.log(this.tmp_res_ob);
      }
  }